import unittest

from mock import MagicMock, patch
import SoftLayer

from jumpgate.compute.drivers.sl.servers import (
    ServerActionV2, ServerV2
)


TENANT_ID = 333333
INSTANCE_ID = 7890782
SERVER_ID = 7777777


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

    @patch('SoftLayer.CCIManager')
    @patch('SoftLayer.CCIManager.get_instance')
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

    @patch('SoftLayer.CCIManager')
    @patch('json.loads')
    def test_on_post_create_fail(self, bodyMock, cciManagerMock):
        e = SoftLayer.SoftLayerAPIError(123, 'abc')
        self.vg_clientMock.createArchiveTransaction.side_effect = e
        bodyMock.return_value = {'createImage': {'name': 'foobar'}}
        instance = ServerActionV2(MagicMock())
        instance.on_post(self.req, self.resp, TENANT_ID, INSTANCE_ID)
        self.assertRaises(SoftLayer.SoftLayerAPIError,
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


class TestServerDetail(unittest.TestCase):
    '''Certain properties such as 'metadata' and 'progress' are not being sent
    in the response, but are specified in the Openstack API reference.
    Will add later when there is support.'''

    def test_init(self):
        app = MagicMock()
        instance = ServerV2(app)
        self.assertEqual(app, instance.app)

    def setUp(self):
        self.req, self.resp = MagicMock(), MagicMock()
        self.clientMock = MagicMock()
        self.req.env = {'sl_client': self.clientMock}

    @patch('SoftLayer.CCIManager.get_instance')
    def perform_server_detail(self, tenant_id, server_id, get_instance_mock):
        instanceSV = ServerV2(app=MagicMock())
        instance = {'status': {'keyName': 'ACTIVE', 'name': 'Active'},
                    'modifyDate': '', 'maxCpu': 2,
                    'createDate': '2014-06-03T15:12:37-06:00',
                    'hostname': 'csh-test', 'sshKeys': [],
                    'id': 4953216,
                    'powerState': {'keyName': 'HALTED', 'name': 'Halted'},
                    'blockDeviceTemplateGroup':
                    {'publicFlag': 0,
                     'name': 'ajiang-jumpgate-sandbox-v1',
                     'userRecordId': 201260,
                     'createDate': '2014-05-10T20:36:51-06:00',
                     'statusId': 1,
                     'globalIdentifier':
                     '9b013d4e-27ce-4673-9607-ef863a88e3a8',
                     'parentId': '', 'transactionId': '', 'id': 141214,
                     'accountId': 333582},
                    'maxMemory': 2048,
                    'accountId': 333582}
        get_instance_mock.return_value = instance
        instanceSV.on_get(self.req, self.resp, tenant_id, server_id)

    def test_on_get_server_detail(self):
        '''Testing the server details'''

        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals(list(self.resp.body.keys()), ['server'])
        self.assertEquals(len(self.resp.body['server']), 20)

    def test_on_get_server_detail_id(self):
        '''checking the type for the property 'id' '''

        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('id' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['id']), str)

    def test_on_get_server_detail_accessIPv4(self):
        '''checking the type for the property 'accessIPv4', and since the
        parameter is hard-coded, we check for the exact response as well'''

        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('accessIPv4' in self.resp.body['server'].keys(),
                          True)
        self.assertEquals(self.resp.body['server']['accessIPv4'], "")

    def test_on_get_server_detail_accessIPv6(self):
        '''checking the type for the property 'accessIPv6', and since the
        parameter is hard-coded, we check for the exact response as well'''

        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('accessIPv6' in self.resp.body['server'].keys(),
                          True)
        self.assertEquals(self.resp.body['server']['accessIPv6'], "")

    def test_on_get_server_detail_addresses(self):
        '''checking the type for the property 'addresses' '''

        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('addresses' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['addresses']), dict)

    def test_on_get_server_detail_flavor(self):
        '''checking the type for the property 'flavor' '''

        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('flavor' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['flavor']), dict)

    def test_on_get_server_detail_image(self):
        '''checking the type for the property 'image' '''

        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('image' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['image']), dict)

    def test_on_get_server_detail_links(self):
        '''checking the type for the property 'links' '''

        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('links' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['links']), list)

    def test_on_get_server_detail_status(self):
        '''checking the type for the property 'status' '''

        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('status' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['status']), str)

    def test_on_get_server_detail_image_name(self):
        '''checking the type for the property 'image_name' '''

        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('image_name' in self.resp.body['server'].keys(),
                          True)
        self.assertEquals(type(self.resp.body['server']['image_name']), str)

    def test_on_get_server_detail_security_groups(self):
        '''checking the type for the property 'security_groups' '''

        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals(
            'security_groups' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['security_groups']),
                          list)

    def test_on_get_server_detail_updated(self):
        '''checking the type for the property 'updated' '''

        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('updated' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['updated']), str)

    def test_on_get_server_detail_created(self):
        '''checking the type for the property 'created' '''

        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('created' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['created']), str)

    def test_on_get_server_detail_hostId(self):
        '''checking the type for the property 'hostId' '''

        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('hostId' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['hostId']), int)

    def test_on_get_server_detail_name(self):
        '''checking the type for the property 'name' '''

        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('name' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['name']), str)

    def test_on_get_server_detail_tenant_id(self):
        '''checking the type for the property 'tenant_id' '''

        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('tenant_id' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['tenant_id']), int)

    def test_on_get_server_detail_progress(self):
        '''checking the type for the property 'user_id' '''

        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('user_id' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['user_id']),
                          type(None))

    def tearDown(self):
        self.req, self.resp, self.app = None, None, None
