from mock import MagicMock
from jumpgate.volume.drivers.sl.volumes import VolumesV1, VolumeV1
from jumpgate.volume.drivers.sl.volumes import VIRTUAL_DISK_IMAGE_TYPE
from SoftLayer import SoftLayerAPIError

import unittest

TENANT_ID = 333333
GUEST_ID = 111111
DISK_IMG_ID = 222222
BLKDEV_MOUNT_ID = '0'
GOOD_VOLUME_ID = "100000"
INVALID_VOLUME_ID = "ABCDEFGDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD"

OP_CODE = {
    'GOOD_PATH': {
        'SIMPLE': 1,
        'RET_VIRT_DISK_IMGS': 4,
        'RET_VIRT_DISK_IMG': 5,
    },
    'BAD_PATH': {
        'VIRT_DISK_IMG_OBJ_INVALID': 2,
        'GET_VIRT_DISK_IMGS_API': 3,
        'RET_BAD_VIRT_GUEST': 6,
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
                        'Account': MagicMock()}}

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


class TestVolumesV1(unittest.TestCase):
    """ Unit tests for class VolumesV1"""

    def setUp(self):

        self.req, self.resp = MagicMock(), MagicMock()
        self.app = VolumesV1()
        self.req.env = {'sl_client': {
                        'Virtual_Disk_Image': MagicMock(),
                        'Virtual_Guest': MagicMock(),
                        'Account': MagicMock()}}

    def test_on_get_for_volume_list_good(self):
        """ Test the good path of list volumes"""
        set_SL_client(self.req)
        self.app.on_get(self.req, self.resp, TENANT_ID)
        self.assertEquals(self.resp.status, 200)

    def test_on_get_for_volume_list_SoftLayerAPIError(self):
        """ Test the bad path of list volumes with SLAPI exception"""
        set_SL_client(
            self.req,
            operation=OP_CODE['BAD_PATH']['GET_VIRT_DISK_IMGS_API'])
        self.app.on_get(self.req, self.resp, TENANT_ID)
        self.assertRaises(SoftLayerAPIError)

    def test_on_get_for_volume_list_good_format_volumes(self):
        """ Test the good path of format_volume func during show volume"""
        set_SL_client(
            self.req,
            operation=OP_CODE['GOOD_PATH']['RET_VIRT_DISK_IMGS'])
        self.app.on_get(self.req, self.resp, TENANT_ID)
        self.assertEquals(list(self.resp.body.keys()), ['volumes'])

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
        #getVirtualDiskImages() SLAPI failure
        setattr(req.env['sl_client']['Account'],
                'getVirtualDiskImages',
                MagicMock(side_effect=SoftLayerAPIError(400,
                                                        "MockFault",
                                                        None)))
    elif operation == OP_CODE['GOOD_PATH']['RET_VIRT_DISK_IMGS']:
        def _return_disk_imgs(*args, **kwargs):
            return [{'typeId': VIRTUAL_DISK_IMAGE_TYPE['SYSTEM'],
                     'blockDevices': [MagicMock()],
                    },
                    {'typeId': VIRTUAL_DISK_IMAGE_TYPE['SWAP'],
                     'blockDevices': [MagicMock()],
                    }]
        setattr(req.env['sl_client']['Account'],
                'getVirtualDiskImages',
                MagicMock(side_effect=_return_disk_imgs))
    elif operation == OP_CODE['GOOD_PATH']['RET_VIRT_DISK_IMG']:
        def _return_disk_img(*args, **kwargs):
            return {'typeId': VIRTUAL_DISK_IMAGE_TYPE['SYSTEM'],
                    'blockDevices': [MagicMock()],
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
