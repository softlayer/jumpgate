from mock import MagicMock, patch
from jumpgate.volume.drivers.sl.volumes import VolumesV1, VolumeV1
from jumpgate.volume.drivers.sl.volumes import VIRTUAL_DISK_IMAGE_TYPE
from SoftLayer import SoftLayerAPIError

import unittest

TENANT_ID = 333333
GUEST_ID = 111111
DISK_IMG_ID = 222222
BLKDEV_MOUNT_ID = '0'
GOOD_VOLUME_ID = "100000"
PROD_PKG_ID = 111111
PRICE_ID = 111111
INVALID_VOLUME_ID = "ABCDEFGDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD"
DISK_CAPACITY = 10
DATACENTER_NAME = "dal05"
DATACENTER_ID = 111111
ORDERID = 4444


OP_CODE = {
    'GOOD_PATH': {
        'SIMPLE': 1,
        'RET_VIRT_DISK_IMGS': 4,
        'RET_VIRT_DISK_IMG': 5,
        'RET_VIRT_DISK_BILL': 7,
        'CREATE_VOLUME': 9,
    },
    'BAD_PATH': {
        'VIRT_DISK_IMG_OBJ_INVALID': 2,
        'GET_VIRT_DISK_IMGS_API': 3,
        'RET_BAD_VIRT_GUEST': 6,
        'RET_VIRT_DISK_EXCP': 8,
    }
}


class TestVolumeV1(unittest.TestCase):
    """ Unit tests for class VolumeV1"""

    def setUp(self):

        self.req, self.resp = MagicMock(), MagicMock()
        self.app = VolumeV1()
        self.req.env = {'sl_client': {
                        'Virtual_Disk_Image': MagicMock(),
                        'Virtual_Guest': MagicMock(),
                        'Account': MagicMock(),
                        'Billing_Item': MagicMock()}}

    def test_on_get_for_volume_unknown_param(self):
        set_SL_client(self.req)
        self.app.on_get(self.req, self.resp, TENANT_ID, None)
        self.assertEquals(self.resp.status, 400)

    def test_on_get_for_volume_details_good(self):
        """ Test the good path of show volume"""
        set_SL_client(self.req)
        self.app.on_get(self.req, self.resp, TENANT_ID, GOOD_VOLUME_ID)
        self.assertEquals(self.resp.status, 200)

    def test_on_get_for_volume_details_invalid_volume_id(self):
        """ Test the bad path of show volume with invalid volume id"""
        set_SL_client(self.req)
        self.app.on_get(self.req, self.resp, TENANT_ID, INVALID_VOLUME_ID)
        self.assertEquals(self.resp.status, 400)

    def test_on_get_for_volume_details_SoftLayerAPIError(self):
        """ Test the bad path of show volume with SLAPI exception"""
        set_SL_client(
            self.req,
            operation=OP_CODE['BAD_PATH']['VIRT_DISK_IMG_OBJ_INVALID'])
        self.app.on_get(self.req, self.resp, TENANT_ID, GOOD_VOLUME_ID)
        self.assertRaises(SoftLayerAPIError)

    def test_on_get_for_volume_details_good_format_volumes(self):
        """ Test the good path of format_volume func during show volume"""
        set_SL_client(
            self.req,
            operation=OP_CODE['GOOD_PATH']['RET_VIRT_DISK_IMG'])
        self.app.on_get(self.req, self.resp, TENANT_ID, GOOD_VOLUME_ID)
        self.assertEquals(list(self.resp.body.keys()), ['volume'])

    def test_on_get_for_volume_details_attachment_SoftLayerAPIError(self):
        """ Test the bad path of _translate_attachment func during show """
        set_SL_client(
            self.req,
            operation=OP_CODE['BAD_PATH']['RET_BAD_VIRT_GUEST'])
        self.app.on_get(self.req, self.resp, TENANT_ID, GOOD_VOLUME_ID)
        self.assertRaises(SoftLayerAPIError)

    def test_on_delete_good_volume_delete(self):
        """ Test the good path of volume delete"""
        set_SL_client(
            self.req,
            operation=OP_CODE['GOOD_PATH']['RET_VIRT_DISK_BILL'])
        self.app.on_delete(self.req, self.resp, TENANT_ID, GOOD_VOLUME_ID)
        self.assertEquals(self.resp.status, 202)

    def test_on_delete_bad_volume_delete_invalud_id(self):
        """ Test the bad path of volume delete with invalid volume id"""
        self.app.on_delete(self.req, self.resp, TENANT_ID, INVALID_VOLUME_ID)
        self.assertEquals(self.resp.status, 400)

    def test_on_delete_volume_getobject_excp(self):
        set_SL_client(
            self.req,
            operation=OP_CODE['BAD_PATH']['RET_VIRT_DISK_EXCP'])
        self.app.on_delete(self.req, self.resp, TENANT_ID, GOOD_VOLUME_ID)
        self.assertRaises(SoftLayerAPIError)


class TestVolumesV1(unittest.TestCase):
    """ Unit tests for class VolumesV1"""

    def setUp(self):

        self.req, self.resp = MagicMock(), MagicMock()
        self.app = VolumesV1()
        self.req.env = {'sl_client': {
                        'Virtual_Disk_Image': MagicMock(),
                        'Virtual_Guest': MagicMock(),
                        'Account': MagicMock(),
                        'Billing_Item': MagicMock(),
                        'Product_Package': MagicMock(),
                        'Product_Order': MagicMock(),
                        'Billing_Order': MagicMock(),
                        'Location_Datacenter': MagicMock()}}

    def test_on_get_for_volume_list_good(self):
        """ Test the good path of list volumes"""
        set_SL_client(self.req)
        self.app.on_get(self.req, self.resp, TENANT_ID)
        self.assertEquals(self.resp.status, 200)

    @patch("jumpgate.volume.drivers.sl.volumes.get_virt_disk_img_mask")
    def test_on_get_for_volume_list_SoftLayerAPIError(self, maskMagic):
        """ Test the bad path of list volumes with SLAPI exception"""
        set_SL_client(
            self.req,
            operation=OP_CODE['BAD_PATH']['GET_VIRT_DISK_IMGS_API'])
        self.app.on_get(self.req, self.resp, TENANT_ID)
        self.assertRaises(SoftLayerAPIError)

    @patch("jumpgate.volume.drivers.sl.volumes.get_virt_disk_img_mask")
    def test_on_get_for_volume_list_good_format_volumes(self, maskMagic):
        """ Test the good path of format_volume func during show volume"""
        set_SL_client(
            self.req,
            operation=OP_CODE['GOOD_PATH']['RET_VIRT_DISK_IMGS'])
        self.app.on_get(self.req, self.resp, TENANT_ID)
        self.assertEquals(list(self.resp.body.keys()), ['volumes'])

    @patch("json.loads")
    def test_on_post_volume_create_bad_request(self, bodyMagic):
        bodyMagic.return_value = {'volume': {'size': 'abcdh'}}
        self.app.on_post(self.req, self.resp, TENANT_ID)
        self.assertEquals(self.resp.status, 400)

    @patch("time.sleep")
    @patch("jumpgate.common.config.CONF")
    @patch("json.loads")
    def test_on_post_volume_create_good(self,
                                        bodyMagic,
                                        CONFMagic,
                                        sleepMagic):
        bodyMagic.return_value = {'volume': {'display_name': 'test',
                                             'size': 1,
                                             'availability_zone': 'dal05'}}
        set_SL_client(
            self.req,
            operation=OP_CODE['GOOD_PATH']['CREATE_VOLUME'])
        self.app.on_post(self.req, self.resp, TENANT_ID)
        self.assertEquals(self.resp.status, 202)

    def tearDown(self):
        self.req, self.resp, self.app = None, None, None


def set_SL_client(req, operation=OP_CODE['GOOD_PATH']['SIMPLE']):
    if operation == OP_CODE['GOOD_PATH']['SIMPLE']:
        # simple good path testing, use default sl_client
        return
    elif operation == OP_CODE['BAD_PATH']['VIRT_DISK_IMG_OBJ_INVALID']:
        # Virtual_Disk_Image.getObject failure.
        req.env['sl_client']['Virtual_Disk_Image'].getObject = \
            MagicMock(side_effect=SoftLayerAPIError(400,
                                                    "MockFault",
                                                    None))
    elif operation == OP_CODE['BAD_PATH']['GET_VIRT_DISK_IMGS_API']:
        # getVirtualDiskImages() SLAPI failure
        setattr(req.env['sl_client']['Account'],
                'getVirtualDiskImages',
                MagicMock(side_effect=SoftLayerAPIError(400,
                                                        "MockFault",
                                                        None)))
    elif operation == OP_CODE['GOOD_PATH']['RET_VIRT_DISK_IMGS']:
        def _return_disk_imgs(*args, **kwargs):
            return [{'typeId': VIRTUAL_DISK_IMAGE_TYPE['SYSTEM'],
                     'blockDevices': [MagicMock()],
                     'localDiskFlag': False,
                    },
                    {'typeId': VIRTUAL_DISK_IMAGE_TYPE['SWAP'],
                     'blockDevices': [MagicMock()],
                     'localDiskFlag': False,
                    }]
        setattr(req.env['sl_client']['Account'],
                'getVirtualDiskImages',
                MagicMock(side_effect=_return_disk_imgs))
    elif operation == OP_CODE['GOOD_PATH']['RET_VIRT_DISK_IMG']:
        def _return_disk_img(*args, **kwargs):
            return {'typeId': VIRTUAL_DISK_IMAGE_TYPE['SYSTEM'],
                    'blockDevices': [MagicMock()],
                     'localDiskFlag': False,
                    }
        req.env['sl_client']['Virtual_Disk_Image'].getObject = \
            MagicMock(side_effect=_return_disk_img)
    elif operation == OP_CODE['BAD_PATH']['RET_BAD_VIRT_GUEST']:
        def _return_disk_img_1(*args, **kwargs):
            return {'typeId': VIRTUAL_DISK_IMAGE_TYPE['SYSTEM'],
                    'blockDevices': [{'guestId': GUEST_ID,
                                      'diskImageId': DISK_IMG_ID,
                                      'device': BLKDEV_MOUNT_ID,
                                     }],
                   }
        req.env['sl_client']['Virtual_Disk_Image'].getObject = \
            MagicMock(side_effect=_return_disk_img_1)
        req.env['sl_client']['Virtual_Guest'].getObject = \
            MagicMock(side_effect=SoftLayerAPIError(400,
                                                    "MockFault",
                                                    None))
    elif operation == OP_CODE['GOOD_PATH']['RET_VIRT_DISK_BILL']:
        def _return_billing_item(*args, **kwargs):
            return {'billingItem': MagicMock()}
        req.env['sl_client']['Virtual_Disk_Image'].getObject = \
            MagicMock(side_effect=_return_billing_item)
    elif operation == OP_CODE['BAD_PATH']['RET_VIRT_DISK_EXCP']:
        req.env['sl_client']['Virtual_Disk_Image'].getObject = \
            MagicMock(side_effect=SoftLayerAPIError(400,
                                                    "MockFault",
                                                    None))
    elif operation == OP_CODE['GOOD_PATH']['CREATE_VOLUME']:
        def _return_all_objects(*args, **kwargs):
            return [{'name': 'Portable Storage',
                     'isActive': 1,
                     'id': PROD_PKG_ID}]

        def _return_prices(*args, **kwargs):
            return [{'id': PROD_PKG_ID,
                     'capacity': DISK_CAPACITY,
                     'prices': [{'id': PRICE_ID}]}]

        def _return_disk_img_2(*args, **kwargs):
            return {'typeId': VIRTUAL_DISK_IMAGE_TYPE['SYSTEM'],
                    'blockDevices': [{'guestId': GUEST_ID,
                                      'diskImageId': DISK_IMG_ID,
                                      'device': BLKDEV_MOUNT_ID,
                                     }],
                   }

        req.env['sl_client']['Product_Package'].getAllObjects = \
            MagicMock(side_effect=_return_all_objects)
        req.env['sl_client']['Product_Package'].getItems = \
            MagicMock(side_effect=_return_prices)
        req.env['sl_client']['Location_Datacenter'].getDatacenters = \
            MagicMock(return_value=[{'name': DATACENTER_NAME,
                                     'id': DATACENTER_ID}])
        req.env['sl_client']['Billing_Order'].getOrderTopLevelItems = \
            MagicMock(
                return_value=[{'billingItem': {'resourceTableId':
                                               DISK_IMG_ID}}])
        req.env['sl_client']['Virtual_Disk_Image'].getObject = \
            MagicMock(side_effect=_return_disk_img_2)
        req.env['sl_client']['Product_Order'].placeOrder = \
            MagicMock(return_value={'orderId': ORDERID})
