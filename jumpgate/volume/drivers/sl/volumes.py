import sys
if sys.version_info < (3, 0):
    import httplib as HTTP
else:
    import http.client as HTTP
import logging
import uuid

from jumpgate.common.error_handling import bad_request, volume_fault


LOG = logging.getLogger(__name__)

VOLUME_MASK = 'id,name,type,typeId,units,storageRepositoryId,capacity,' + \
              'description,createDate,blockDevices,' + \
              'storageRepository.datacenter'

MOUNTPOINT = {'0': "First Disk(boot)",
              '2': "Second Disk",
              '3': "Third Disk",
              '4': "Fourth Disk",
              '5': "Fifth Disk"}

VIRTUAL_DISK_IMAGE_TYPE = {
    'SYSTEM': 241,
    'SWAP': 246
}

# openstack is use uuid.uuid4() to generate UUID.
OPENSTACK_VOLUME_UUID_LEN = len(str(uuid.uuid4()))


class VolumesV2(object):
    """ This code has been deprecated. It will be removed once
    the portable storage device based volume functions are implemented.
    """
    def on_get(self, req, resp, tenant_id):
        resp.body = {'volumes': []}

    def on_post(self, req, resp, tenant_id):
        resp.body = {'volume': {}}


class VolumeV1(object):
    """ class VolumeV1 supports the following cinder volume endpoints:
    GET /v1/{tenant_id}/volumes/{volume_id}    -- Shows a specified volume
    DELETE /v1/{tenant_id}/volumes/{volume_id} -- Delete a specified volume
    """

    def on_get(self, req, resp, tenant_id, volume_id):

        client = req.env['sl_client']

        if volume_id and len(volume_id) <= OPENSTACK_VOLUME_UUID_LEN:
            # show volume details by volume id
            # /v1/{tenant_id}/volumes/{volume_id}
            self._show_volume(tenant_id, volume_id, client, req, resp)
        else:
            return bad_request(resp, message="Malformed request body")

    def _show_volume(self, tenant_id, volume_id, client, req, resp):
        """Show the details of a particular portable storage device.
        :param tenant_id: SoftLayer tenant id
        :param volume_id: id of the portable storage device
        :param client: SoftLayer Client
        :param req: Http Request body
        :param resp: Http Response body
        :param return: Http status
        """

        vol = client['Virtual_Disk_Image']
        volinfo = None
        try:
            volinfo = vol.getObject(id=volume_id, mask=VOLUME_MASK)
        except Exception as e:
            return volume_fault(resp, e.faultString, code=HTTP.NOT_FOUND)

        resp.status = HTTP.OK
        resp.body = {'volume':
                     format_volume(tenant_id,
                                   volinfo,
                                   client,
                                   showDetails=True)}


class VolumesV1(object):
    """ class VolumesV1 supports the following cinder volume endpoints:
    POST /v1/{tenant_id}/volumes    -- create volume
    GET /v1/{tenant_id}/volumes     -- Lists simple volume entities
    GET /v1/{tenant_id}/volumes/detail -- Lists details for volume entities
    """

    def on_get(self, req, resp, tenant_id):

        client = req.env['sl_client']

        # list volumes API:
        # /v1/{tenant_id}/volumes/detail
        self._list_volumes(tenant_id, client, req, resp)

    def _list_volumes(self, tenant_id, client, req, resp):
        """ Retrieve all the SoftLayer portable storage devices of
        a given tenant and generate the Cinder volume list. The swap
        device(SoftLayer Virtual_Disk_Image with typeID 246) will not be
        listed. The VSI's boot disk is also SoftLayer portable storage
        device. The VSI boot disk will always be shown as attached and
        it will be removed during VSI destory due to its ephemeral nature.

        :param tenant_id: SoftLayer tenant id
        :param client: SoftLayer Client
        :param req: Http Request body
        :param resp: Http Response body
        :param return: Http status
        """

        # Get SoftLayer getVirtualDiskImages() function
        try:
            _getVirtualDiskImages = getattr(client['Account'],
                                            'getVirtualDiskImages')
            # filter out the swap disk from the retrived portable storage
            # devices
            vols = [x for x in _getVirtualDiskImages(mask=VOLUME_MASK)
                    if x['typeId'] != VIRTUAL_DISK_IMAGE_TYPE['SWAP']]
            resp.body = {"volumes":
                         [format_volume(tenant_id,
                                        vol,
                                        client) for vol in vols]}

            resp.status = HTTP.OK

        except Exception as e:
            return volume_fault(resp, e.faultString)


def format_volume(tenant_id, volume, client, showDetails=False, version=1):
    LOG.info("volume info: %s", str(volume))
    blkdevs = volume.get('blockDevices', None)
    attachment = []
    bootable = 'false'

    for blkdev in blkdevs:
        attachment.append(
            _translate_attachment(blkdev, client, showDetails=showDetails))
        if blkdev.get('bootableFlag'):
            bootable = 'true'

    zone = ""
    store_repo = volume.get('storageRepository')
    if store_repo and store_repo.get('datacenter'):
        zone = store_repo['datacenter'].get('name')

    volinfo = {
        "id": volume.get('id'),
        "display_name": volume.get('name'),
        "display_description": volume.get('description'),
        "size": volume.get('capacity'),
        "volume_type": str(volume.get('typeId')),
        "metadata": {},
        "snapshot_id": None,
        "attachments": attachment,
        "bootable": bootable,
        "availability_zone": zone,
        "created_at": volume.get('createDate'),
    }

    # Cinder volume API version greater than v1.
    if version > 1:
        volinfo.update(
            {"os-vol-tenant-attr:tenant_id": tenant_id})

    return volinfo


def _translate_attachment(blkdev, client, showDetails=False):
    d = {}

    d['id'] = blkdev.get('diskImageId')
    d['server_id'] = ""
    d['host_name'] = ""

    guestId = blkdev.get('guestId')

    if guestId and showDetails:
        vs = client['Virtual_Guest']
        try:
            vsinfo = vs.getObject(id=blkdev.get('guestId'))
            hostname = vsinfo.get('fullyQualifiedDomainName')
            d['server_id'] = str(blkdev.get('guestId'))
            d['host_name'] = hostname

        except Exception:
            pass
    else:
        d['server_id'] = str(blkdev.get('guestId'))
        d['host_name'] = ""

    d['mountpoint'] = MOUNTPOINT.get(blkdev.get('device'), "UNKNOWN")
    return d
