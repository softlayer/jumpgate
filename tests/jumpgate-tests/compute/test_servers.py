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

    @mock.patch('jumpgate.compute.drivers.sl.servers.SoftLayer.VSManager')
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

    @mock.patch('jumpgate.compute.drivers.sl.servers.SoftLayer.VSManager')
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
                '.VSManager.upgrade')
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

    @mock.patch('SoftLayer.VSManager.list_instances')
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
                'metadata': {},
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


class TestServerDetail(unittest.TestCase):
    '''Certain properties such as 'metadata' and 'progress' are not being sent
    in the response, but are specified in the Openstack API reference.
    Will add later when there is support.
    '''
    @mock.patch('jumpgate.compute.drivers.sl.servers.SoftLayer.VSManager'
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
        self.assertEquals(len(list(self.resp.body['server'])), 21)

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
        self.assertEquals(type(self.resp.body['server']['hostId']), str)

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
        self.assertEquals(type(self.resp.body['server']['tenant_id']), str)

    def test_on_get_server_detail_progress(self):
        '''checking the type for the property 'user_id'
        '''

        self.perform_server_detail(TENANT_ID, SERVER_ID)
        self.assertEquals('user_id' in self.resp.body['server'].keys(), True)
        self.assertEquals(type(self.resp.body['server']['user_id']),
                          str)


class TestServersV2(unittest.TestCase):
    def setUp(self):

        self.app = mock.MagicMock()
        self.instance = servers.ServersV2(self.app, FLAVOR_LIST)
        self.payload = {}
        self.body = {'server': {'name': 'testserver',
                                'imageRef':
                                    'a1783280-6b1f',
                                'availability_zone': 'dal05', 'flavorRef': '1',
                                'max_count': 1, 'min_count': 1,
                                'networks': [{'uuid': 489586},
                                             {'uuid': 489588}]}}
        self.body_string = '{"server": {"name": "testserver", ' \
                           '"imageRef": "a1783280-6b1f", ' \
                           '"availability_zone": "dal05", ' \
                           '"flavorRef": "1", ' \
                           '"max_count": 1, ' \
                           '"min_count": 1, ' \
                           '"networks": [{"uuid": 489586}, {"uuid": 489588}]}}'
        self.client, env = get_client_env()

    def test_init(self):
        self.assertEqual(self.app, self.instance.app)

    def test_handle_flavor(self):
        self.instance._handle_flavor(self.payload, self.body)
        self.assertEqual(self.payload['cpus'], 1)
        self.assertEqual(self.payload['memory'], 1024)
        self.assertEqual(self.payload['local_disk'], False)

    def test_handle_sshkeys_empty(self):
        self.instance._handle_sshkeys(self.payload, self.body, self.client)
        self.assertEqual(self.payload['ssh_keys'], [])

    @mock.patch('SoftLayer.managers.sshkey.SshKeyManager.list_keys')
    def test_handle_sshkeys_nonempty_valid(self, sshKeyManagerList):
        sshKeyManagerList.return_value = [{'id': 'fakeid'}]
        self.body['server']['key_name'] = 'fakename'
        self.instance._handle_sshkeys(self.payload, self.body, self.client)
        self.assertEqual(self.payload['ssh_keys'], ['fakeid'])

    @mock.patch('SoftLayer.managers.sshkey.SshKeyManager.list_keys')
    def test_handle_sshkeys_nonempty_invalid(self, sshKeyManagerList):
        sshKeyManagerList.return_value = []
        self.body['server']['key_name'] = 'fakename'
        should_fail = False
        try:
            self.instance._handle_sshkeys(self.payload, self.body, self.client)
            should_fail = True
        except Exception:
            pass
        if should_fail:
            self.fail('Exception expected')

    def test_handle_user_data_empty(self):
        self.instance._handle_user_data(self.payload, self.body)
        self.assertEqual(self.payload['userdata'], '{}')

    def test_handle_user_data_metadata(self):
        self.body['server']['metadata'] = 'metadata'
        self.instance._handle_user_data(self.payload, self.body)
        self.assertEqual(self.payload['userdata'], '{"metadata": "metadata"}')

    def test_handle_user_data_user_data(self):
        self.body['server']['user_data'] = 'user_data'
        self.instance._handle_user_data(self.payload, self.body)
        self.assertEqual(self.payload['userdata'],
                         '{"user_data": "user_data"}')

    def test_handle_user_data_personality(self):
        self.body['server']['personality'] = 'personality'
        self.instance._handle_user_data(self.payload, self.body)
        self.assertEqual(self.payload['userdata'],
                         '{"personality": "personality"}')

    def test_handle_datacenter(self):
        self.body['server']['availability_zone'] = 'dal05'
        self.instance._handle_datacenter(self.payload, self.body)
        self.assertEqual(self.payload['datacenter'], 'dal05')

    @mock.patch('oslo.config.cfg.ConfigOpts.GroupAttr')
    def test_handle_datacenter_empty(self, conf_mock):
        self.body['server']['availability_zone'] = None
        conf_mock.return_value = {
            "default_availability_zone": None
        }
        should_fail = False
        try:
            self.instance._handle_datacenter(self.payload, self.body)
            should_fail = True
        except Exception:
            pass
        if should_fail:
            self.fail('Exception expected')

    def test_handle_network_valid_public_private_ids(self):

        self.instance._handle_network(self.payload, self.client,
                                      [{'uuid': 489586}, {'uuid': 489588}])
        self.assertEqual(self.payload['public_vlan'], 489588)
        self.assertEqual(self.payload['private_vlan'], 489586)
        self.assertEqual(self.payload['private'], False)

    def test_handle_network_invalid_too_many(self):
        should_fail = False
        try:
            self.instance._handle_network(self.payload, self.client,
                                          [{'uuid': 489588}, {'uuid': 489586},
                                           {'uuid': 43}])
            should_fail = True
        except Exception:
            pass
        if should_fail:
            self.fail('Exception excepted, too many arguments')

    def test_handle_network_invalid_id_order(self):
        self.client['Account'].getPrivateNetworkVlans.return_value = []
        should_fail = False
        try:
            self.instance._handle_network(self.payload, self.client,
                                          [{'uuid': 489588}, {'uuid': 489586}])
            should_fail = True
        except Exception:
            pass
        if should_fail:
            self.fail('Exception excepted')

    def test_handle_network_invalid_id_format(self):
        self.client['Account'].getPrivateNetworkVlans.return_value = []
        should_fail = False
        try:
            self.instance._handle_network(self.payload, self.client,
                                          [{'uuid': 'bad_network'}])
            should_fail = True
        except Exception:
            pass
        if should_fail:
            self.fail('Exception excepted')

    def test_handle_network_invalid_id_format_public(self):
        self.client['Account'].getPrivateNetworkVlans.return_value = []
        should_fail = False
        try:
            self.instance._handle_network(self.payload, self.client,
                                          [{'uuid': '489586'},
                                           {'uuid': 'bad_pub_id'}])
            should_fail = True
        except Exception:
            pass
        if should_fail:
            self.fail('Exception excepted')

    def test_handle_network_valid_private_ids(self):
        self.client['Account'].getPrivateNetworkVlans.return_value = [489586]
        self.instance._handle_network(self.payload, self.client,
                                      [{'uuid': 489586}])
        self.assertEqual(self.payload['private_vlan'], 489586)
        self.assertEqual(self.payload['private'], True)

    def test_handle_network_valid_ids(self):
        self.client['Account'].getPrivateNetworkVlans.return_value = [489586]
        self.client['Account'].getPublicNetworkVlans.return_value = [489588]
        self.instance._handle_network(self.payload, self.client,
                                      [{'uuid': 489586}, {'uuid': 489588}])
        self.assertEqual(self.payload['private_vlan'], 489586)
        self.assertEqual(self.payload['public_vlan'], 489588)
        self.assertEqual(self.payload['private'], False)

    def test_handle_network_valid_public(self):
        self.instance._handle_network(self.payload, self.client,
                                      [{'uuid': 'public'}])
        self.assertEqual(self.payload['private'], False)

    def test_handle_network_valid_private(self):
        self.instance._handle_network(self.payload, self.client,
                                      [{'uuid': 'private'}])
        self.assertEqual(self.payload['private'], True)

    def test_handle_network_invalid_private(self):
        should_fail = False
        try:
            self.instance._handle_network(self.payload, self.client,
                                          [{'uuid': 'private'},
                                           {'uuid': 'public'}])
            should_fail = True
        except Exception:
            pass
        if should_fail:
            self.fail('Exception excepted')

    def test_handle_network_invalid_public(self):
        should_fail = False
        try:
            self.instance._handle_network(self.payload, self.client,
                                          [{'uuid': 'public'},
                                           {'uuid': 'private'}])
            should_fail = True
        except Exception:
            pass
        if should_fail:
            self.fail('Exception excepted')

    @mock.patch('SoftLayer.managers.vs.VSManager.create_instance')
    def test_on_post_valid(self, create_instance_mock):
        create_instance_mock.return_value = \
            {"domain": "jumpgate.com",
             "maxMemory": 1024,
             "maxCpuUnits": 'CORE',
             "maxCpu": 1, "metricPollDate": "",
             "createDate": "2014-06-23T14:44:27-05:00",
             "hostname": "testserver",
             "startCpus": 1,
             "lastPowerStateId": "",
             "lastVerifiedDate": "",
             "statusId": 1001,
             "globalIdentifier": "8bfd7c70-5ee4-4581-a2c1-6ae8986fc97a",
             "dedicatedAccountHostOnlyFlag": False,
             "modifyDate": '',
             "accountId": str(333582),
             "id": 5139276,
             "fullyQualifiedDomainName": "testserver2.jumpgate.com"}
        client, env = get_client_env(body=self.body_string)
        req = falcon.Request(env)
        resp = falcon.Response()
        self.instance.on_post(req, resp, 'tenant_id')
        self.assertEqual(resp.status, 202)
        self.assertEqual(resp.body['server']['id'], str(5139276))

    @mock.patch('SoftLayer.managers.vs.VSManager.create_instance')
    def test_on_post_invalid_create(self, create_instance_mock):
        create_instance_mock.side_effect = Exception('badrequest')
        client, env = get_client_env(body=self.body_string)
        req = falcon.Request(env)
        resp = falcon.Response()
        self.instance.on_post(req, resp, 'tenant_id')
        self.assertEqual(resp.status, 400)

    def test_on_post_invalid(self):
        self.body['server']['networks'][0]['uuid'] = 'invalid'
        client, env = get_client_env(
            body='{"server": {"name": "testserver", '
                 '"imageRef": "a1783280-6b1f", "flavorRef": "invalid"}}')
        req = falcon.Request(env)
        resp = falcon.Response()
        self.instance.on_post(req, resp, 'tenant_id')
        self.assertEqual(resp.status, 400)
