import unittest
import falcon
from falcon.testing import helpers
import mock
import SoftLayer

from jumpgate.compute.drivers.sl import flavor_list_loader
from jumpgate.compute.drivers.sl import servers


TENANT_ID = 333333
INSTANCE_ID = 7890782
SERVER_ID = 7777777
FLAVOR_LIST = flavor_list_loader.Flavors.get_flavors(app=mock.MagicMock())


def get_client_env(**kwargs):
    client = mock.MagicMock()
    env = helpers.create_environ(**kwargs)
    env['sl_client'] = client
    return client, env


class TestServersServerActionV2(unittest.TestCase):

    def perform_server_action(self, body_str, tenant_id,
                              instance_id, flavors):
        self.client, self.env = get_client_env(body=body_str)
        self.vg_clientMock = self.client['Virtual_Guest']
        self.req = falcon.Request(self.env)
        self.resp = falcon.Response()
        instance = servers.ServerActionV2(app=mock.MagicMock(),
                                          flavors=flavors)
        instance.on_post(self.req, self.resp, tenant_id, instance_id)

    @mock.patch('jumpgate.compute.drivers.sl.servers.SoftLayer.CCIManager')
    def test_on_post_create(self, cciMock):
        body_str = '{"createImage": {"name": "foobar"}}'
        self.perform_server_action(body_str, TENANT_ID,
                                   INSTANCE_ID, flavors=FLAVOR_LIST)
        client_cat = self.vg_clientMock.createArchiveTransaction
        client_cat.assert_called_with("foobar", [], 'Auto-created by '
                                      'OpenStack compatibility layer',
                                      id=INSTANCE_ID)
        filterMock = {'privateBlockDeviceTemplateGroups':
                      {'name': {'operation': "foobar"},
                       'createDate': {'operation': 'orderBy',
                                      'options': [{'name': 'sort',
                                                   'value': ['DESC']}], }}}
        acc = self.client['Account'].getPrivateBlockDeviceTemplateGroups
        acc.assert_called_with(mask='id, globalIdentifier',
                               filter=filterMock, limit=1)
        self.assertEquals(self.resp.status, 202)

    @mock.patch('jumpgate.compute.drivers.sl.servers.SoftLayer.CCIManager')
    def test_on_post_create_fail(self, cciMock):
        client, env = get_client_env(body='{"createImage": \
        {"name": "foobar"}}')
        vg_clientMock = client['Virtual_Guest']
        e = SoftLayer.SoftLayerAPIError(123, 'abc')
        vg_clientMock.createArchiveTransaction.side_effect = e
        req = falcon.Request(env)
        resp = falcon.Response()
        instance = servers.ServerActionV2(app=mock.MagicMock(),
                                          flavors=FLAVOR_LIST)
        instance.on_post(req, resp, TENANT_ID, INSTANCE_ID)
        self.assertRaises(SoftLayer.SoftLayerAPIError,
                          vg_clientMock.createArchiveTransaction)
        self.assertEquals(resp.status, 500)

    def test_on_post_powerOn(self):
        body_str = '{"os-start": "None"}'
        self.perform_server_action(body_str, TENANT_ID, INSTANCE_ID,
                                   flavors=FLAVOR_LIST)
        self.assertEquals(self.resp.status, 202)
        self.vg_clientMock.powerOn.assert_called_with(id=INSTANCE_ID)

    def test_on_post_powerOff(self):
        body_str = '{"os-stop": "None"}'
        self.perform_server_action(body_str, TENANT_ID, INSTANCE_ID,
                                   flavors=FLAVOR_LIST)
        self.assertEquals(self.resp.status, 202)
        self.vg_clientMock.powerOff.assert_called_with(id=INSTANCE_ID)

    def test_on_post_reboot_soft(self):
        body_str = '{"reboot": {"type": "SOFT"}}'
        self.perform_server_action(body_str, TENANT_ID, INSTANCE_ID,
                                   flavors=FLAVOR_LIST)
        self.assertEquals(self.resp.status, 202)
        self.vg_clientMock.rebootSoft.assert_called_with(id=INSTANCE_ID)

    def test_on_post_reboot_hard(self):
        body_str = '{"reboot": {"type": "HARD"}}'
        self.perform_server_action(body_str, TENANT_ID, INSTANCE_ID,
                                   flavors=FLAVOR_LIST)
        self.assertEquals(self.resp.status, 202)
        self.vg_clientMock.rebootHard.assert_called_with(id=INSTANCE_ID)

    def test_on_post_reboot_default(self):
        body_str = '{"reboot": {"type": "DEFAULT"}}'
        self.perform_server_action(body_str, TENANT_ID, INSTANCE_ID,
                                   flavors=FLAVOR_LIST)
        self.assertEquals(self.resp.status, 202)
        self.vg_clientMock.rebootDefault.assert_called_with(id=INSTANCE_ID)

    @mock.patch('jumpgate.compute.drivers.sl.servers.SoftLayer'
                '.CCIManager.upgrade')
    def test_on_post_resize(self, cciMock):
        body_str = '{"resize": {"flavorRef": "2"}}'
        self.perform_server_action(body_str, TENANT_ID, INSTANCE_ID,
                                   flavors=FLAVOR_LIST)
        cciMock.assert_called_with(INSTANCE_ID, cpus=1, memory=1)
        self.assertEquals(self.resp.status, 202)

    def test_on_post_resize_invalid(self):
        body_str = '{"resize": {"flavorRef": "17"}}'
        self.perform_server_action(body_str, TENANT_ID, INSTANCE_ID,
                                   flavors=FLAVOR_LIST)
        self.assertEquals(self.resp.status, 400)

    def test_on_post_confirm_resize(self):
        body_str = '{"confirmResize": "None"}'
        self.perform_server_action(body_str, TENANT_ID, INSTANCE_ID,
                                   flavors=FLAVOR_LIST)
        self.assertEquals(self.resp.status, 204)

    def test_on_post_body_empty(self):
        body_str = '{}'
        self.perform_server_action(body_str, TENANT_ID, INSTANCE_ID,
                                   flavors=FLAVOR_LIST)
        self.assertEquals(self.resp.status, 400)
        self.assertEquals(self.resp.body['badRequest']['message'],
                          'Malformed request body')

    def test_on_post_instanceid_empty(self):
        body_str = '{"os-stop": "None"}'
        self.perform_server_action(body_str, TENANT_ID, '',
                                   flavors=FLAVOR_LIST)
        self.assertEquals(self.resp.status, 404)
        self.assertEquals(self.resp.body['notFound']['message'],
                          'Invalid instance ID specified.')

    def test_on_post_instanceid_none(self):
        body_str = '{"os-start": "None"}'
        self.perform_server_action(body_str, TENANT_ID, None,
                                   flavors=FLAVOR_LIST)
        self.assertEquals(self.resp.status, 404)

    def test_on_post_malformed_body(self):
        body_str = '{"os_start": "None"}'
        self.perform_server_action(body_str, TENANT_ID, INSTANCE_ID,
                                   flavors=FLAVOR_LIST)
        self.assertEquals(self.resp.status, 400)


class TestServersServersDetailV2(unittest.TestCase):

    @mock.patch('SoftLayer.CCIManager.list_instances')
    def test_on_get(self, mockListInstance):
        client, env = get_client_env()
        href = u'http://localhost:5000/compute/v2/333582/servers/4846014'
        dict = {'status': 'ACTIVE',
                'updated': '2014-05-23T10:58:29-05:00',
                'hostId': 4846014,
                'user_id': 206942,
                'addresses': {
                    'public': [{
                        'version': 4,
                        'addr': '23.246.195.197',
                        'OS-EXT-IPS:type': 'fixed'}],
                    'private': [{
                        'version': 4,
                        'addr': '10.107.38.132',
                        'OS-EXT-IPS:type': 'fixed'}]},
                'links': [{
                    'href': href,
                    'rel': 'self'}],
                'created': '2014-05-23T10:57:07-05:00',
                'tenant_id': 333582,
                'image_name': '',
                'OS-EXT-STS:power_state': 1,
                'accessIPv4': '',
                'accessIPv6': '',
                'OS-EXT-STS:vm_state': 'ACTIVE',
                'OS-EXT-STS:task_state': None,
                'flavor': {
                    'id': '1',
                    'links': [{
                        'href': 'http://localhost:5000/compute/v2/flavors/1',
                        'rel': 'bookmark'}]},
                'OS-EXT-AZ:availability_zone': 154820,
                'id': '4846014',
                'security_groups': [{
                    'name': 'default'}],
                'name': 'minwoo-metis',
                }
        status = {'keyName': 'ACTIVE', 'name': 'Active'}
        pwrState = {'keyName': 'RUNNING', 'name': 'Running'}
        sshKeys = []
        dataCenter = {'id': 154820, 'name': 'dal06', 'longName': 'Dallas 6'}
        orderItem = {'itemId': 858,
                     'setupFee': '0',
                     'promoCodeId': '',
                     'oneTimeFeeTaxRate': '.066',
                     'description': '2 x 2.0 GHz Cores',
                     'laborFee': '0',
                     'oneTimeFee': '0',
                     'itemPriceId': '1641',
                     'setupFeeTaxRate': '.066',
                     'order': {
                         'userRecordId': 206942,
                         'privateCloudOrderFlag': False},
                     'laborFeeTaxRate': '.066',
                     'categoryCode': 'guest_core',
                     'setupFeeDeferralMonths': 12,
                     'parentId': '',
                     'recurringFee': '0',
                     'id': 34750548,
                     'quantity': '',
                     }
        billingItem = {'modifyDate': '2014-06-05T08:37:01-05:00',
                       'resourceTableId': 4846014,
                       'hostName': 'minwoo-metis',
                       'recurringMonths': 1,
                       'orderItem': orderItem,
                       }

        mockListInstance.return_value = {'billingItem': billingItem,
                                         'datacenter': dataCenter,
                                         'powerState': pwrState,
                                         'sshKeys': sshKeys,
                                         'status': status,
                                         'accountId': 'foobar',
                                         'id': '1234',
                                         'createDate': 'foobar',
                                         'hostname': 'foobar',
                                         'modifyDate': 'foobar'
                                         }
        req = falcon.Request(env)
        resp = falcon.Response()
        instance = servers.ServersDetailV2(app=mock.MagicMock())
        instance.on_get(req, resp, TENANT_ID)
        self.assertEquals(set(resp.body['servers'][0].keys()),
                          set(dict.keys()))
        self.assertEquals(resp.status, 200)


class TestServersV2(unittest.TestCase):

    def perform_server_action(self, req, resp, tenant_id, flavors):
        instance = servers.ServersV2(app=mock.MagicMock(), flavors=flavors)
        instance.on_post(req, resp, tenant_id)

    @mock.patch('jumpgate.compute.drivers.sl.servers.SoftLayer.CCIManager'
                '.create_instance')
    def test_on_post_change_port_speed_default(self, ccIMock):
        '''Test that if port speed is not specified in the flavor, then the
        instance is created with the default port speed by SoftLayer
        '''
        client, env = get_client_env(body='{"server": \
        {"name": "unit-test", \
        "imageRef": "9b013d4e-27ce-4673-9607-ef863a88e3a8", \
        "availability_zone": "dal06", "flavorRef": "1", \
        "max_count": 1, "min_count": 1}}')
        test_dict = {1: {"disk-type": "SAN",
                         "name": "1 vCPU, 2GB ram, \
                         100GB, SAN",
                         "ram": 2048, "cpus": 1, "disk": 100,
                         "id": "1"}}
        ccIMock.return_value = {'id': '333333'}
        req = falcon.Request(env)
        resp = falcon.Response()
        self.perform_server_action(req, resp, TENANT_ID, test_dict)
        payload = {
            'hostname': u'unit-test',
            'domain': 'jumpgate.com',
            'cpus': 1,
            'memory': 2048,
            'local_disk': False,
            'hourly': True,
            'datacenter': u'dal06',
            'image_id': u'9b013d4e-27ce-4673-9607-ef863a88e3a8',
            'ssh_keys': [],
            'private': False,
            'userdata': '{}',
        }
        ccIMock.assert_called_with(**payload)
        self.assertEquals(resp.status, 202)
        self.assertEquals(list(resp.body.keys()), ['server'])
        self.assertEquals(len(resp.body['server']), 3)

    @mock.patch('jumpgate.compute.drivers.sl.servers.SoftLayer.CCIManager'
                '.create_instance')
    def test_on_post_change_port_speed_1000(self, ccIMock):
        '''Test that if user specifies a port speed in the flavor, then that
        port speed is used when creating the instance
        '''
        client, env = get_client_env(body='{"server": \
        {"name": "unit-test", \
        "imageRef": "9b013d4e-27ce-4673-9607-ef863a88e3a8", \
        "availability_zone": "dal06", "flavorRef": "1", \
        "max_count": 1, "min_count": 1}}')
        test_dict = {1: {"disk-type": "SAN",
                         "name": "1 vCPU, 2GB ram, 100GB, SAN",
                         "ram": 2048, "cpus": 1, "disk": 100,
                         "id": "1", "portspeed": 1000}}
        ccIMock.return_value = {'id': '333333'}
        req = falcon.Request(env)
        resp = falcon.Response()
        self.perform_server_action(req, resp, TENANT_ID, test_dict)
        payload = {
            'hostname': u'unit-test',
            'domain': 'jumpgate.com',
            'cpus': 1,
            'memory': 2048,
            'local_disk': False,
            'hourly': True,
            'datacenter': u'dal06',
            'image_id': u'9b013d4e-27ce-4673-9607-ef863a88e3a8',
            'ssh_keys': [],
            'private': False,
            'userdata': '{}',
            'nic_speed': 1000,
        }
        ccIMock.assert_called_with(**payload)
        self.assertEquals(resp.status, 202)
        self.assertEquals(list(resp.body.keys()), ['server'])
        self.assertEquals(len(resp.body['server']), 3)


class TestServerDetail(unittest.TestCase):
    '''Certain properties such as 'metadata' and 'progress' are not being sent
    in the response, but are specified in the Openstack API reference.
    Will add later when there is support.
    '''
    @mock.patch('jumpgate.compute.drivers.sl.servers.SoftLayer.CCIManager'
                '.get_instance')
    def perform_server_detail(self, tenant_id, server_id, get_instance_mock):
        self.client, self.env = get_client_env()
        instanceSV = servers.ServerV2(app=mock.MagicMock())
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
        self.req = falcon.Request(self.env)
        self.resp = falcon.Response()
        instanceSV.on_get(self.req, self.resp, tenant_id, server_id)

    def test_on_get_server_detail(self):
        '''Testing the server details
        '''
        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals(list(self.resp.body.keys()), ['server'])
        self.assertEquals(len(list(self.resp.body['server'])), 20)

    def test_on_get_server_detail_id(self):
        '''checking the type for the property 'id'
        '''
        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('id' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['id']), str)

    def test_on_get_server_detail_accessIPv4(self):
        '''checking the type for the property 'accessIPv4', and since the
        parameter is hard-coded, we check for the exact response as well
        '''
        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('accessIPv4' in self.resp.body['server'].keys(),
                          True)
        self.assertEquals(self.resp.body['server']['accessIPv4'], "")

    def test_on_get_server_detail_accessIPv6(self):
        '''checking the type for the property 'accessIPv6', and since the
        parameter is hard-coded, we check for the exact response as well
        '''
        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('accessIPv6' in self.resp.body['server'].keys(),
                          True)
        self.assertEquals(self.resp.body['server']['accessIPv6'], "")

    def test_on_get_server_detail_addresses(self):
        '''checking the type for the property 'addresses'
        '''
        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('addresses' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['addresses']), dict)

    def test_on_get_server_detail_flavor(self):
        '''checking the type for the property 'flavor'
        '''
        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('flavor' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['flavor']), dict)

    def test_on_get_server_detail_image(self):
        '''checking the type for the property 'image'
        '''
        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('image' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['image']), dict)

    def test_on_get_server_detail_links(self):
        '''checking the type for the property 'links'
        '''
        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('links' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['links']), list)

    def test_on_get_server_detail_status(self):
        '''checking the type for the property 'status'
        '''
        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('status' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['status']), str)

    def test_on_get_server_detail_image_name(self):
        '''checking the type for the property 'image_name'
        '''
        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('image_name' in self.resp.body['server'].keys(),
                          True)
        self.assertEquals(type(self.resp.body['server']['image_name']), str)

    def test_on_get_server_detail_security_groups(self):
        '''checking the type for the property 'security_groups'
        '''
        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('security_groups' in self.resp.body['server'].keys(),
                          True)
        self.assertEquals(type(self.resp.body['server']['security_groups']),
                          list)

    def test_on_get_server_detail_updated(self):
        '''checking the type for the property 'updated'
        '''
        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('updated' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['updated']), str)

    def test_on_get_server_detail_created(self):
        '''checking the type for the property 'created'
        '''
        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('created' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['created']), str)

    def test_on_get_server_detail_hostId(self):
        '''checking the type for the property 'hostId'
        '''
        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('hostId' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['hostId']), int)

    def test_on_get_server_detail_name(self):
        '''checking the type for the property 'name'
        '''
        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('name' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['name']), str)

    def test_on_get_server_detail_tenant_id(self):
        '''checking the type for the property 'tenant_id'
        '''
        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('tenant_id' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['tenant_id']), int)

    def test_on_get_server_detail_progress(self):
        '''checking the type for the property 'user_id'
        '''
        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('user_id' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['user_id']),
                          type(None))
