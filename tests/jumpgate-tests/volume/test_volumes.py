import mock
import unittest
import json

import falcon
from falcon.testing import helpers

from jumpgate.volume.drivers.sl import volumes
from jumpgate.volume.drivers import volume_types_loader
import SoftLayer

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

EXPECTED = {
    "volume_types": [{
        "id": "241",
        "name": "san",
        "extra_specs": {
            "capabilities:volume_backend_name": "sjc01",
            "drivers:display_name": "default",
            "drivers:san_backed_disk": True,
            "drivers:exact_capacity": False,
            }
    }, ]
}

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


def _set_up_req_resp_body(**kwargs):
    env = helpers.create_environ(**kwargs)
    req = falcon.Request(env)
    resp = falcon.Response()
    client = mock.MagicMock()
    env['sl_client'] = client
    return client, env, req, resp


def _set_up_vol_types_vtl(json_str):
    vtl = volume_types_loader.VolumeTypesLoader(json_str)
    volume_types = vtl.get_volume_types()
    return vtl, volume_types


class TestVolumeTypesV1Success(unittest.TestCase):

    def test_on_get_success(self):
        client, env, req, resp = _set_up_req_resp_body()
        self.vtl, volume_types = _set_up_vol_types_vtl(json.dumps(EXPECTED))
        app = volumes.VolumeTypesV1(volume_types)
        app.on_get(req, resp, TENANT_ID)
        self.assertEquals(resp.status, 200)
        self.assertEquals(set(resp.body.keys()),
                          set(EXPECTED.keys()))
        for v_type in resp.body['volume_types']:
            self.assertEquals(set(v_type['extra_specs'].keys()),
                              set(EXPECTED['volume_types'][0]
                                  ['extra_specs'].keys()))
            self.assertEquals(set(v_type.keys()),
                              set(EXPECTED['volume_types'][0].keys()))


@mock.patch('jumpgate.volume.drivers.volume_types_loader.LOG.error')
class TestVolumeTypesLoader(unittest.TestCase):

    def _check_expected(self, volume_types):
        self.assertEquals(set(volume_types),
                          set(EXPECTED))
        self.assertEquals(
            set(volume_types['volume_types'][0]),
            set(EXPECTED['volume_types'][0]))

    def test_init_success(self, logMock):
        self.vtl, volume_types = _set_up_vol_types_vtl(
            json.dumps(EXPECTED))
        logMock.assert_not_called()
        self._check_expected(volume_types)

    def test_init_json_error(self, logMock):
        bad_json_str = '['
        self.vtl, volume_types = _set_up_vol_types_vtl(bad_json_str)
        logMock.assert_called_with('JSON FORMATTING ERROR in'
                                   ' jumpgate.conf or config.py!')
        self.assertEquals(volume_types,
                          {'volume_types': []})

    def test_init_wrong_parent_key(self, logMock):
        bad_key = '{"badkey": []}'
        self.vtl, volume_types = _set_up_vol_types_vtl(
            json.dumps(bad_key))
        logMock.assert_called_with('Unable to load "volume_types"'
                                   ' from configuration file.')
        self._check_expected(volume_types)

    def test_init_lookup_error(self, logMock):
        no_exspec = {'volume_types': [{'id': '1', 'name': 'san'}]}
        self.vtl, volume_types = _set_up_vol_types_vtl(json.dumps(
            no_exspec))
        logMock.assert_called_with('Expects volume_types with'
                                   ' "extra_specs" key.  '
                                   'Replaced with default values.')
        self._check_expected(volume_types)

    def test_init_multiple_errors(self, logMock):
        expec_no_children = {
            'volume_types': [{
                'id': '1',
                'name': 'san',
                'extra_specs': {}}]}
        self.vtl, volume_types = _set_up_vol_types_vtl(
            json.dumps(expec_no_children))
        logMock.assert_called_with('Replaced capabilities:volume_backend'
                                   '_name, drivers:display_name, '
                                   'drivers:san_backed_disk, '
                                   'drivers:exact_capacity with '
                                   'default values')
        self._check_expected(volume_types)


class TestVolumeV1(unittest.TestCase):
    """ Unit tests for class VolumeV1"""

    def setUp(self):
        self.client, self.env, self.req, self.resp = _set_up_req_resp_body()
        self.app = volumes.VolumeV1()

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
        self.assertRaises(SoftLayer.SoftLayerAPIError)

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
        self.assertRaises(SoftLayer.SoftLayerAPIError)

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
        self.assertRaises(SoftLayer.SoftLayerAPIError)


class TestVolumesV1(unittest.TestCase):
    """ Unit tests for class VolumesV1"""

    def setUp(self):
        self.body = {
            'volume': {
                'display_name': 'test',
                'size': 10,
                'availability_zone': 'sjc01',
                'volume_type': 'san',
            }
        }

    def test_on_get_for_volume_list_good(self):
        """ Test the good path of list volumes"""
        client, env, req, resp = _set_up_req_resp_body()
        self.vtl, volume_types = _set_up_vol_types_vtl(json.dumps(EXPECTED))
        app = volumes.VolumesV1(volume_types)
        app.on_get(req, resp, TENANT_ID)
        self.assertEquals(resp.status, 200)

    def test_on_get_for_volume_list_SoftLayerAPIError(self):
        """ Test the bad path of list volumes with SLAPI exception"""
        client, env, req, resp = _set_up_req_resp_body()
        self.vtl, volume_types = _set_up_vol_types_vtl(json.dumps(EXPECTED))
        app = volumes.VolumesV1(volume_types)
        set_SL_client(
            req,
            operation=OP_CODE['BAD_PATH']['GET_VIRT_DISK_IMGS_API'])
        app.on_get(req, resp, TENANT_ID)
        self.assertRaises(SoftLayer.SoftLayerAPIError)

    def test_on_get_for_volume_list_good_format_volumes(self):
        """ Test the good path of format_volume func during show volume"""
        client, env, req, resp = _set_up_req_resp_body()
        self.vtl, volume_types = _set_up_vol_types_vtl(json.dumps(EXPECTED))
        app = volumes.VolumesV1(volume_types)
        set_SL_client(
            req,
            operation=OP_CODE['GOOD_PATH']['RET_VIRT_DISK_IMGS'])
        app.on_get(req, resp, TENANT_ID)
        self.assertEquals(list(resp.body.keys()), ['volumes'])

    def test_on_post_volume_create_bad_request(self):
        self.body = {'volume': {'size': 'abcdh'}}
        client, env, req, resp = _set_up_req_resp_body(body=
                                                       json.dumps(self.body))
        self.vtl, volume_types = _set_up_vol_types_vtl(json.dumps(EXPECTED))
        app = volumes.VolumesV1(volume_types)
        app.on_post(req, resp, TENANT_ID)
        self.assertEquals(resp.status, 400)

    def test_on_post_volume_create_good(self):
        self.body['volume_type'] = None
        client, env, req, resp =\
            _set_up_req_resp_body(body=json.dumps(self.body))
        set_SL_client(
            req,
            operation=OP_CODE['GOOD_PATH']['CREATE_VOLUME'])
        self.vtl, volume_types = _set_up_vol_types_vtl(json.dumps(EXPECTED))
        app = volumes.VolumesV1(volume_types)
        app.on_post(req, resp, TENANT_ID)
        self.assertEquals(list(resp.body.keys()), ["volume"])
        self.assertEquals(resp.status, 202)

    def test_on_post_volume_create_v_type_present_name_valid(self):
        client, env, req, resp =\
            _set_up_req_resp_body(body=json.dumps(self.body))
        set_SL_client(
            req,
            operation=OP_CODE['GOOD_PATH']['CREATE_VOLUME'])
        self.vtl, volume_types = _set_up_vol_types_vtl(json.dumps(EXPECTED))
        app = volumes.VolumesV1(volume_types)
        app.on_post(req, resp, TENANT_ID)
        self.assertEquals(list(resp.body.keys()), ["volume"])
        self.assertEquals(resp.status, 202)

    @mock.patch("jumpgate.volume.drivers.sl.volumes.error_handling.bad_request")  # noqa
    def test_on_post_volume_create_v_type_present_name_invalid(self,
                                                               mock_bad_req,
                                                               ):
        self.body['volume']['volume_type'] = 'bad'
        client, env, req, resp =\
            _set_up_req_resp_body(body=json.dumps(self.body))
        set_SL_client(
            req,
            operation=OP_CODE['GOOD_PATH']['CREATE_VOLUME'])
        self.vtl, volume_types = _set_up_vol_types_vtl(json.dumps(EXPECTED))
        app = volumes.VolumesV1(volume_types)
        app.on_post(req, resp, TENANT_ID)
        mock_bad_req.assert_called_with(resp,
                                        'Specify a volume with'
                                        ' a valid name')
        self.assertEquals(resp.status, 400)

    def test_on_post_volume_create_good_v_type_round_size(self):
        self.body['volume']['size'] = 1
        client, env, req, resp =\
            _set_up_req_resp_body(body=json.dumps(self.body))
        set_SL_client(
            req,
            operation=OP_CODE['GOOD_PATH']['CREATE_VOLUME'])
        self.vtl, volume_types = _set_up_vol_types_vtl(json.dumps(EXPECTED))
        app = volumes.VolumesV1(volume_types)
        app.on_post(req, resp, TENANT_ID)
        self.assertEquals(list(resp.body.keys()), ["volume"])
        self.assertTrue('size' in resp.body['volume'])
        self.assertNotEquals(resp.body['volume']['size'], 1)
        self.assertEquals(resp.status, 202)

    def test_on_post_volume_create_v_type_exact_size_fail(self):
        self.body['volume']['size'] = 1
        client, env, req, resp =\
            _set_up_req_resp_body(body=json.dumps(self.body))
        set_SL_client(
            req,
            operation=OP_CODE['GOOD_PATH']['CREATE_VOLUME'])
        modify_expected = EXPECTED.copy()
        me = modify_expected['volume_types'][0]['extra_specs']
        me['drivers:exact_capacity'] = True
        self.vtl, volume_types = _set_up_vol_types_vtl(json.dumps(
            modify_expected))
        app = volumes.VolumesV1(volume_types)
        app.on_post(req, resp, TENANT_ID)
        self.assertEquals(resp.status, 400)


def set_SL_client(req, operation=OP_CODE['GOOD_PATH']['SIMPLE']):
    if operation == OP_CODE['GOOD_PATH']['SIMPLE']:
        # simple good path testing, use default sl_client
        return
    elif operation == OP_CODE['BAD_PATH']['VIRT_DISK_IMG_OBJ_INVALID']:
        # Virtual_Disk_Image.getObject failure.
        req.env['sl_client']['Virtual_Disk_Image'].getObject = \
            mock.MagicMock(side_effect=
                           SoftLayer.SoftLayerAPIError(400,
                                                       "MockFault",
                                                       None))
    elif operation == OP_CODE['BAD_PATH']['GET_VIRT_DISK_IMGS_API']:
        # getVirtualDiskImages() SLAPI failure
        setattr(req.env['sl_client']['Account'],
                'getVirtualDiskImages',
                mock.MagicMock(side_effect=
                               SoftLayer.SoftLayerAPIError(400,
                                                           "MockFault",
                                                           None)))
    elif operation == OP_CODE['GOOD_PATH']['RET_VIRT_DISK_IMGS']:
        def _return_disk_imgs(*args, **kwargs):
            return [
                {'typeId': volumes.VIRTUAL_DISK_IMAGE_TYPE['SYSTEM'],
                 'blockDevices': [mock.MagicMock()],
                 'localDiskFlag': False,
                 },
                {'typeId': volumes.VIRTUAL_DISK_IMAGE_TYPE['SWAP'],
                 'blockDevices': [mock.MagicMock()],
                 'localDiskFlag': False,
                 }]
        setattr(req.env['sl_client']['Account'],
                'getVirtualDiskImages',
                mock.MagicMock(side_effect=_return_disk_imgs))
    elif operation == OP_CODE['GOOD_PATH']['RET_VIRT_DISK_IMG']:
        def _return_disk_img(*args, **kwargs):
            return {'typeId': volumes.VIRTUAL_DISK_IMAGE_TYPE['SYSTEM'],
                    'blockDevices': [mock.MagicMock()],
                    'localDiskFlag': False, }
        req.env['sl_client']['Virtual_Disk_Image'].getObject = \
            mock.MagicMock(side_effect=_return_disk_img)
    elif operation == OP_CODE['BAD_PATH']['RET_BAD_VIRT_GUEST']:
        def _return_disk_img_1(*args, **kwargs):
            return {
                'typeId': volumes.VIRTUAL_DISK_IMAGE_TYPE['SYSTEM'],
                'blockDevices': [{
                    'guestId': GUEST_ID,
                    'diskImageId': DISK_IMG_ID,
                    'device': BLKDEV_MOUNT_ID,
                }],
            }
        req.env['sl_client']['Virtual_Disk_Image'].getObject = \
            mock.MagicMock(side_effect=_return_disk_img_1)
        req.env['sl_client']['Virtual_Guest'].getObject = \
            mock.MagicMock(side_effect=
                           SoftLayer.SoftLayerAPIError(400,
                                                       "MockFault",
                                                       None))
    elif operation == OP_CODE['GOOD_PATH']['RET_VIRT_DISK_BILL']:
        def _return_billing_item(*args, **kwargs):
            return {'billingItem': mock.MagicMock()}
        req.env['sl_client']['Virtual_Disk_Image'].getObject = \
            mock.MagicMock(side_effect=_return_billing_item)
    elif operation == OP_CODE['BAD_PATH']['RET_VIRT_DISK_EXCP']:
        req.env['sl_client']['Virtual_Disk_Image'].getObject = \
            mock.MagicMock(side_effect=
                           SoftLayer.SoftLayerAPIError(400,
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
            return {
                'typeId': volumes.VIRTUAL_DISK_IMAGE_TYPE['SYSTEM'],
                'blockDevices': [{
                    'guestId': GUEST_ID,
                    'diskImageId': DISK_IMG_ID,
                    'device': BLKDEV_MOUNT_ID,
                }],
            }

        req.env['sl_client']['Product_Package'].getAllObjects = \
            mock.MagicMock(side_effect=_return_all_objects)
        req.env['sl_client']['Product_Package'].getItems = \
            mock.MagicMock(side_effect=_return_prices)
        req.env['sl_client']['Location_Datacenter'].getDatacenters = \
            mock.MagicMock(return_value=[{'name': DATACENTER_NAME,
                                         'id': DATACENTER_ID}])
        req.env['sl_client']['Billing_Order'].getOrderTopLevelItems = \
            mock.MagicMock(
                return_value=[{'billingItem': {'resourceTableId':
                                               DISK_IMG_ID}}])
        req.env['sl_client']['Virtual_Disk_Image'].getObject = \
            mock.MagicMock(side_effect=_return_disk_img_2)
        req.env['sl_client']['Product_Order'].placeOrder = \
            mock.MagicMock(return_value={'orderId': ORDERID})
