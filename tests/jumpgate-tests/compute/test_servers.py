from mock import MagicMock, patch
from jumpgate.compute.drivers.sl.servers import (ServerActionV2,
                                                 SoftLayerAPIError,
                                                 )
import unittest

TENANT_ID = 333333
INSTANCE_ID = 7890782


class TestServersServerActionV2(unittest.TestCase):

    def test_init(self):
        app = MagicMock()
        instance = ServerActionV2(app)
        self.assertEqual(app, instance.app)

    def setUp(self):
        self.req, self.resp = MagicMock(), MagicMock()
        self.vg_clientMock = MagicMock()
        self.req.env = {'sl_client': {
                        'Virtual_Guest': self.vg_clientMock,
                        'Account': MagicMock()}}

    def perform_server_action(self, tenant_id, instance_id):
        instance = ServerActionV2(app=None)
        instance.on_post(self.req, self.resp, tenant_id, instance_id)

    @patch('jumpgate.compute.drivers.sl.servers.CCIManager')
    @patch('jumpgate.compute.drivers.sl.servers.CCIManager.get_instance')
    @patch('json.loads')
    def test_on_post_create(self, bodyMock, cciGetInstanceMock,
                            cciManagerMock):
        bodyMock.return_value = {'createImage': {'name': 'foobar'}}
        cciGetInstanceMock.return_value = {'blockDevices':
                                           [{'device': 0},
                                            {'device': 1}]}
        instance = ServerActionV2(MagicMock())
        instance.on_post(self.req, self.resp, TENANT_ID, INSTANCE_ID)
        self.assertEquals(self.resp.status, 202)

    @patch('jumpgate.compute.drivers.sl.servers.CCIManager')
    @patch('json.loads')
    def test_on_post_create_fail(self, bodyMock, cciManagerMock):
        e = SoftLayerAPIError(123, 'abc')
        self.vg_clientMock.createArchiveTransaction.side_effect = e
        bodyMock.return_value = {'createImage': {'name': 'foobar'}}
        instance = ServerActionV2(MagicMock())
        instance.on_post(self.req, self.resp, TENANT_ID, INSTANCE_ID)
        self.assertRaises(SoftLayerAPIError,
                          self.vg_clientMock.createArchiveTransaction)
        self.assertEquals(self.resp.status, 500)

    @patch('json.loads')
    def test_on_post_powerOn(self, bodyMock):
        bodyMock.return_value = {'os-start': None}
        self.perform_server_action(TENANT_ID, INSTANCE_ID)
        self.assertEquals(self.resp.status, 202)
        self.vg_clientMock.powerOn.assert_called_with(id=INSTANCE_ID)

    @patch('json.loads')
    def test_on_post_powerOff(self, bodyMock):
        bodyMock.return_value = {'os-stop': None}
        self.perform_server_action(TENANT_ID, INSTANCE_ID)
        self.assertEquals(self.resp.status, 202)
        self.vg_clientMock.powerOff.assert_called_with(id=INSTANCE_ID)

    @patch('json.loads')
    def test_on_post_reboot_soft(self, bodyMock):
        bodyMock.return_value = {'reboot': {'type': 'SOFT'}}
        self.perform_server_action(TENANT_ID, INSTANCE_ID)
        self.assertEquals(self.resp.status, 202)
        self.vg_clientMock.rebootSoft.assert_called_with(id=INSTANCE_ID)

    @patch('json.loads')
    def test_on_post_reboot_hard(self, bodyMock):
        bodyMock.return_value = {'reboot': {'type': 'HARD'}}
        self.perform_server_action(TENANT_ID, INSTANCE_ID)
        self.assertEquals(self.resp.status, 202)
        self.vg_clientMock.rebootHard.assert_called_with(id=INSTANCE_ID)

    @patch('json.loads')
    def test_on_post_reboot_default(self, bodyMock):
        bodyMock.return_value = {'reboot': {'type': 'DEFAULT'}}
        self.perform_server_action(TENANT_ID, INSTANCE_ID)
        self.assertEquals(self.resp.status, 202)
        self.vg_clientMock.rebootDefault.assert_called_with(id=INSTANCE_ID)

    @patch('json.loads')
    @patch('SoftLayer.managers.vs.VSManager.upgrade')
    def test_on_post_resize(self, upgradeMock, bodyMock):
        bodyMock.return_value = {"resize": {"flavorRef": "2"}}
        upgradeMock.return_value = True
        self.perform_server_action(TENANT_ID, INSTANCE_ID)
        self.assertEquals(self.resp.status, 202)

    @patch('json.loads')
    def test_on_post_resize_invalid(self, bodyMock):
        bodyMock.return_value = {"resize": {"flavorRef": "17"}}
        self.perform_server_action(TENANT_ID, INSTANCE_ID)
        self.assertEquals(self.resp.status, 400)

    @patch('json.loads')
    def test_on_post_confirm_resize(self, bodyMock):
        bodyMock.return_value = {'confirmResize': None}
        self.perform_server_action(TENANT_ID, INSTANCE_ID)
        self.assertEquals(self.resp.status, 204)

    @patch('json.loads')
    def test_on_post_body_empty(self, bodyMock):
        bodyMock.return_value = {}
        self.perform_server_action(TENANT_ID, INSTANCE_ID)
        self.assertEquals(self.resp.status, 400)
        self.assertEquals(self.resp.body['badRequest']
                          ['message'], 'Malformed request body')

    @patch('json.loads')
    def test_on_post_instanceid_empty(self, bodyMock):
        bodyMock.return_value = {'os-stop': None}
        self.perform_server_action(TENANT_ID, '')
        self.assertEquals(self.resp.status, 404)
        self.assertEquals(self.resp.body['notFound']
                          ['message'], 'Invalid instance ID specified.')

    @patch('json.loads')
    def test_on_post_instanceid_none(self, bodyMock):
        bodyMock.return_value = {'os-start': None}
        self.perform_server_action(TENANT_ID, None)
        self.assertEquals(self.resp.status, 404)

    @patch('json.loads')
    def test_on_post_malformed_body(self, bodyMock):
        bodyMock.return_value = {'os_start': None}
        self.perform_server_action(TENANT_ID, INSTANCE_ID)
        self.assertEquals(self.resp.status, 400)

    def tearDown(self):
        self.req, self.resp, self.vg_clientMock = None, None, None
