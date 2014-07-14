import json
import uuid

import six

from jumpgate.common import error_handling

HTTP = six.moves.http_client  # pylint: disable=E1101

# openstack is use uuid.uuid4() to generate UUID.
OPENSTACK_VOLUME_UUID_LEN = len(str(uuid.uuid4()))


class OSVolumeAttachmentsV2(object):
    """class OSVolumeAttachmentsV2 supports the following nova volume endpoints

    GET /v2/{tenant_id}/servers/{server_id}/os-volume_attachments
        -- Lists the volume attachments for a specified server.
    POST /v2/{tenant_id}/servers/{server_id}/os-volume_attachments
        -- Attaches a specified volume to a specified server.
    """

    def on_get(self, req, resp, tenant_id, instance_id):
        '''Lists volume attachments for the instance.'''
        vg_client = req.env['sl_client']['Virtual_Guest']
        try:
            instance_id = int(instance_id)
        except Exception:
            return error_handling.not_found(resp,
                                            "Invalid instance ID specified.")

        try:
            blkDevices = vg_client.getBlockDevices(mask='id, diskImage.type',
                                                   id=instance_id)

            vols = [format_volume_attachment(vol['diskImage']['id'],
                                             instance_id,
                                             '')
                    for vol in blkDevices
                    if vol['diskImage']['type']['keyName'] != 'SWAP']
            resp.body = {"volumeAttachments": vols}
        except Exception as e:
            error_handling.volume_fault(resp, e.faultString)

    def on_post(self, req, resp, tenant_id, instance_id):
        '''Attaches a specified volume to a specified server.'''
        body = json.loads(req.stream.read().decode())

        if (len(body) == 0 or 'volumeAttachment' not in body or
                'volumeId' not in body['volumeAttachment']):
            return error_handling.bad_request(resp, message="Malformed "
                                                            "request body")

        vg_client = req.env['sl_client']['Virtual_Guest']

        try:
            instance_id = int(instance_id)
        except Exception:
            return error_handling.not_found(resp,
                                            "Invalid instance ID specified.")

        volume_id = body['volumeAttachment']['volumeId']
        if volume_id and len(volume_id) > OPENSTACK_VOLUME_UUID_LEN:
            return error_handling.bad_request(resp, message="Malformed "
                                              "request body")

        vdi_client = req.env['sl_client']['Virtual_Disk_Image']
        volinfo = None

        # first let's check if the volume is already attached
        try:
            volinfo = vdi_client.getObject(id=volume_id,
                                           mask='blockDevices')
            blkDevices = volinfo['blockDevices']
            if (len(blkDevices) > 0):
                guestId_list = [blkDevice['guestId'] for blkDevice
                                in blkDevices]
                for guest_id in guestId_list:
                    if (guest_id == instance_id):
                        return error_handling.volume_fault(
                            resp,
                            'The requested disk image is already attached to '
                            'this guest.',
                            code=HTTP.BAD_REQUEST)
                    else:
                        return error_handling.volume_fault(
                            resp,
                            'The requested disk image is already attached to '
                            'another guest.',
                            code=HTTP.BAD_REQUEST)
        except Exception as e:
            return error_handling.volume_fault(resp,
                                               e.faultString,
                                               code=HTTP.NOT_FOUND)

        try:
            # providing different size doesn't seem to have any impact on the
            # outcome hence using 10 as default size.
            disk_check = vg_client.checkHostDiskAvailability(10,
                                                             id=instance_id)
        except Exception:
            disk_check = True

        try:
            if disk_check:
                sl_transaction = vg_client.attachDiskImage(volume_id,
                                                           id=instance_id)
                resp.body = {"volumeAttachment":
                             {"device": "",
                              "id": sl_transaction['id'],
                              "serverId": instance_id,
                              "volumeId": volume_id}}
                resp.status = HTTP.ACCEPTED
            else:
                return error_handling.volume_fault(
                    resp,
                    'Action causes migration to a new host. Migration is not '
                    'allowed.',
                    code=HTTP.BAD_REQUEST)
        except Exception as e:
            error_handling.volume_fault(resp, e.faultString)


class OSVolumeAttachmentV2(object):
    """class OSVolumeAttachmentsV2 supports the following nova volume endpoints

    GET /v2/{tenant_id}/servers/{server_id}/os-volume_attachments/
    {attachment_id} -- Shows details for the specified volume attachment.

    DELETE /v2/{tenant_id}/servers/{server_id}/os-volume_attachments/
    {attachment_id}
        -- Detaches a specified volume attachment from a specified server.
    """
    def on_get(self, req, resp, tenant_id, instance_id, volume_id):
        '''Shows details for the specified volume attachment.'''
        try:
            instance_id = int(instance_id)
        except Exception:
            return error_handling.not_found(resp,
                                            "Invalid instance ID specified.")

        if volume_id and len(volume_id) > OPENSTACK_VOLUME_UUID_LEN:
            return error_handling.bad_request(resp,
                                              message="Malformed request body")

        # since detail has the same info as the input request params, we can
        # just return the values back in the response using the request params.
        # But instead we will do sanity check to ensure the volume_id belongs
        # to the instance.
        vg_client = req.env['sl_client']['Virtual_Guest']
        try:
            blkDevices = vg_client.getBlockDevices(mask='id, diskImage.type',
                                                   id=instance_id)
            vols = [x for x in blkDevices
                    if x['diskImage']['type']['keyName'] != 'SWAP']
            for vol in vols:
                json_response = None
                vol_disk_id = vol['diskImage']['id']
                if str(vol_disk_id) == volume_id:
                    json_response = {"volumeAttachment":
                                     {"device": "", "id": vol_disk_id,
                                      "serverId": instance_id,
                                      "volumeId": vol_disk_id}}
                    break
            if json_response:
                resp.body = json_response
            else:
                return error_handling.volume_fault(resp, 'Invalid volume id.',
                                                   code=HTTP.BAD_REQUEST)
        except Exception as e:
            return error_handling.volume_fault(resp, e.faultString)

    def on_delete(self, req, resp, tenant_id, instance_id, volume_id):
        """Detach the requested volume from the specified instance."""
        try:
            instance_id = int(instance_id)
        except Exception:
            return error_handling.not_found(resp,
                                            "Invalid instance ID specified.")

        if volume_id and len(volume_id) > OPENSTACK_VOLUME_UUID_LEN:
            return error_handling.bad_request(resp,
                                              message="Malformed request body")

        vdi_client = req.env['sl_client']['Virtual_Disk_Image']

        # first let's check if the volume is already attached
        try:
            volinfo = vdi_client.getObject(id=volume_id, mask='blockDevices')
            blkDevices = volinfo['blockDevices']
            if len(blkDevices) > 0:
                guestId_list = [blkDevice['guestId'] for blkDevice
                                in blkDevices]
                for guest_id in guestId_list:
                    if guest_id == instance_id:
                        try:
                            # detach the volume here
                            vg_client = req.env['sl_client']['Virtual_Guest']
                            vg_client.detachDiskImage(volume_id,
                                                      id=instance_id)
                            break
                        except Exception as e:
                            error_handling.volume_fault(resp,
                                                        e.faultString)
                    else:
                        return error_handling.volume_fault(
                            resp,
                            'The requested disk image is attached to another '
                            'guest and cannot be detached.',
                            code=HTTP.BAD_REQUEST)

        except Exception as e:
            return error_handling.volume_fault(resp, e.faultString,
                                               code=500)

        resp.status = HTTP.ACCEPTED


def format_volume_attachment(volume_id, instance_id, device_name):
    return {"device": device_name, "id": volume_id, "serverId": instance_id,
            "volumeId": volume_id}
