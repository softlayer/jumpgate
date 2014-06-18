import sys
if sys.version_info < (3, 0):
    import httplib as HTTP
else:
    import http.client as HTTP
import json
import logging
import uuid
import time

from jumpgate.common.config import CONF
from jumpgate.common.error_handling import bad_request, volume_fault, error
from jumpgate.common.utils import lookup
from SoftLayer import SoftLayerAPIError

LOG = logging.getLogger(__name__)

CONTAINER_VIRT_DISK = 'SoftLayer_Container_Product_Order_Virtual_Disk_Image'

MOUNTPOINT = {'0': "First Disk(boot)",
              '2': "Second Disk",
              '3': "Third Disk",
              '4': "Fourth Disk",
              '5': "Fifth Disk"}

VIRTUAL_DISK_IMAGE_TYPE = {
    'SYSTEM': 241,
    'SWAP': 246
}

RETRY_COUNT = 3
WAIT_TIME = 2

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

    def on_delete(self, req, resp, tenant_id, volume_id):

        client = req.env['sl_client']

        if volume_id and len(volume_id) <= OPENSTACK_VOLUME_UUID_LEN:
            # show volume details by volume id
            # /v1/{tenant_id}/volumes/{volume_id}
            self._delete_volume(tenant_id, volume_id, client, req, resp)
        else:
            return bad_request(resp, message="Invalid volume Id")


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
            volinfo = vol.getObject(id=volume_id,
                                    mask=get_virt_disk_img_mask())
        except Exception as e:
            return volume_fault(resp, e.faultString, code=HTTP.NOT_FOUND)

        resp.status = HTTP.OK
        resp.body = {'volume':
                     format_volume(tenant_id,
                                   volinfo,
                                   client,
                                   showDetails=True)}

    def _delete_volume(self, tenant_id, volume_id, client, req, resp):

        virtual_disk = client['Virtual_Disk_Image']

        try:
            item = virtual_disk.getObject(id=volume_id, mask='billingItem')
        except SoftLayerAPIError as e:
            return volume_fault(resp, e.faultString, code=HTTP.NOT_FOUND)

        billingItemId = item['billingItem']['id']
        billing = client['Billing_Item']
        # Reason is from this document:
        # https://sldn.softlayer.com/reference/services/
        #       SoftLayer_Billing_Item/cancelItem
        reason = "No longer needed"
        billing.cancelItem(True, True, reason, id=billingItemId)
        resp.status = HTTP.ACCEPTED


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

    def on_post(self, req, resp, tenant_id):
        """ Create volume (SL Portable storage) """
        client = req.env['sl_client']

        try:
            body = json.loads(req.stream.read().decode())
            # required field in the create volume payload
            volreq = body['volume']
            name = (CONF['volume']['volume_name_prefix'] +
                    lookup(body, 'volume', 'display_name'))


            # size is required option for volume create. Throw type exception
            # if it is invalid
            size = int(volreq['size'])
            # availability_zone is optional, don't throw exception if
            # it is not available
            availability_zone = (lookup(body, 'volume', 'availability_zone')
                                 or
                                 CONF['volume']['default_availability_zone'])
            volume_type = lookup(body, 'volume', 'volume_type')

        except Exception:
            return bad_request(resp, 'Malformed request body')

        try:
            volinfo = self._create_volume(tenant_id, client, resp,
                                          size, name=name,
                                          zone=availability_zone,
                                          volume_type=volume_type)


            resp.status = HTTP.ACCEPTED

            resp.body = {'volume':
                         format_volume(tenant_id, volinfo, client)}
            resp.body.update({'status': 'creating'})

        except SoftLayerAPIError as e:
            return error(resp,
                         "SoftLayerAPIError",
                         e.faultString,
                         code=HTTP.INTERNAL_SERVER_ERROR)
        except Exception as e:
            return volume_fault(resp, str(e))

    def _create_volume(self, tenant_id, client, resp, size,
                       name=None, zone=None, volume_type=None):
        """ Please Order to create a SL portable storage(SAN)
        :param tenant_id: SoftLayer tenant id
        :param client: SoftLayer Client
        :param resp: Http Response body
        :param size: volume size in GB
        :param name: volume name
        :param zone: volume availability_zone
        :param volume_type: volume type
        :param return: cinder volume info
        """
        def _find_product_package_id():
            """ return SL product page id """
            prod_pkg = client['Product_Package'].getAllObjects()
            prod = [item for item in prod_pkg
                    if item['name'].lower() == "portable storage" and
                    item['isActive'] == 1]
            if prod:
                return prod[0]['id']
            else:
                return None

        def _match_portable_storage_prices(packageId, size):
            """ match the SL portable storage capacity that closet
            to the requested size and return the prices"""
            prod_pkg = client['Product_Package']
            price_list = prod_pkg.getItems(id=packageId,
                                           mask='prices.id')
            # each item in price_list looks like this:
            # {'capacity': '150',
            #  'description': '150 GB (SAN)',
            #  'id': 1221,
            #  'prices': [{'id': 2262}],
            #  'softwareDescriptionId': '',
            #  'units': 'GB',
            #  'upgradeItemId': ''}
            price_matrix = {}

            for x in price_list:
                price_matrix.update({int(x['capacity']): x['prices']})

            # find the closet capacity to the requested size
            capacity_idx = min(price_matrix, key=lambda x: abs(x - size))

            return price_matrix[capacity_idx]

        def _find_availibility_zone_location(zone):

            # make sure there is an availability_zone selected
            zonename = zone if zone else 'dal05'

            datacenter = client['Location_Datacenter']
            locations = dict(map(lambda x: (x['name'], x['id']),
                             datacenter.getDatacenters(mask="name,id")))
            # use dal05 as default datacenter. The disk cannot be found if
            # being ordered without datacenter.
            return locations.get(zonename, locations.get('dal05'))

        def _get_volume_id_from_ordered_items(order_id):
            """ The SL placeOrder only returns the receipt not the
            ordered items itself. Need to find the portable disk id
            from the ordered item to generate the respond body for
            volume create"""

            bill = client['Billing_Order']
            count = 0
            while count < RETRY_COUNT:
                items = bill.getOrderTopLevelItems(id=order_id,
                                                   mask='billingItem')
                # There is only one disk ordered per volume create.
                try:
                    # it seems billingItem may not be available
                    # immediately after order. Retry as needed.
                    volume_id = items[0]['billingItem']['resourceTableId']
                    if volume_id:
                        break
                except Exception:
                    time.sleep(WAIT_TIME * count)
                    count += 1

            return volume_id

        pkgid = _find_product_package_id()
        prices = _match_portable_storage_prices(pkgid, size)
        loc = _find_availibility_zone_location(zone)

        data = {'complexType': CONTAINER_VIRT_DISK,
                'prices': prices,
                'packageId': pkgid,
                'location': loc,
                'diskDescription': name}

        LOG.debug("Portable storage order payload: %s" % str(data))
        product = client['Product_Order']
        product.overifyOrder(data)
        order = product.placeOrder(data)
        LOG.debug("Portable Storage order receipt: %s" % str(order))
        volume_id = _get_volume_id_from_ordered_items(order['orderId'])
        virtual_disk = client['Virtual_Disk_Image']
        volinfo = virtual_disk.getObject(id=volume_id,
                                            mask=get_virt_disk_img_mask())
        return volinfo

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
            vols = [x for x in
                    _getVirtualDiskImages(mask=get_virt_disk_img_mask())
                    if x['typeId'] != VIRTUAL_DISK_IMAGE_TYPE['SWAP'] and
                    not x['localDiskFlag']]
            resp.body = {"volumes":
                         [format_volume(tenant_id,
                                        vol,
                                        client) for vol in vols]}
            resp.status = HTTP.OK

        except Exception as e:
            return volume_fault(resp, str(e))


def format_volume(tenant_id, volume, client, showDetails=False, version=1):
    def _get_volume_status(volume):

        status = None
        if 'billingItem' in volume:
            if len(volume['blockDevices']) > 0:
                # The blockDevices is not empty. It is attached to VSI.
                status = "in-use"
            else:
                status = "available"
        else:
            # For the volume that doesn't have billingItem is is either
            # othered with VSI or it has been cancelled.
            if len(volume['blockDevices']) > 0:
                status = "in-use"
            else:
                status = "deleting"
        return status

    LOG.info("volume info: %s", str(volume))
    blkdevs = volume.get('blockDevices', None)
    attachment = []
    bootable = 'false'
    status = _get_volume_status(volume)

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
        "status": status,
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
            vsinfo = vs.getObject(id=blkdev.get('guestId'),
                                  mask='billingItem')
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


def get_virt_disk_img_mask():
    mask = [
        'id',
        'name',
        'type',
        'typeId',
        'units',
        'storageRepositoryId',
        'capacity',
        'description',
        'createDate',
        'blockDevices',
        'storageRepository.datacenter',
        'billingItem',
        'localDiskFlag']
    return 'mask[%s]' % ','.join(mask)
