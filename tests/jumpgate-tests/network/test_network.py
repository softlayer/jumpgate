import unittest

from mock import MagicMock
from jumpgate.network.drivers.sl.networks import NetworksV2, NetworkV2


class TestNetworkV2(unittest.TestCase):
    def setUp(self):
        self.req, self.resp = MagicMock(), MagicMock()
        self.account_client_mock = MagicMock()
        self.net_vlan_mock = MagicMock()
        self.req.env = {
            'sl_client': {
                'Account': self.account_client_mock,
                'Network_Vlan': self.net_vlan_mock,
            },
            'auth': {
                'tenant_id': 999999
            },
        }
        self.req.env['sl_client'][
            'Account'].getPublicNetworkVlans.return_value = [{'id': 11},
                                                             {'id': 5555}]

    def side_effect_show(*args):
        if args[1] == 'name' and args[0].param == 'name':
            return '123321'
        else:
            return 'id'

    def perform_network_action(self, network_id):
        """Initaite the NetworkV2 Instance"""
        instance = NetworkV2()
        instance.on_get(self.req, self.resp, network_id)

    def check_response_body(self, resp_body_network):
        self.assertEqual(resp_body_network['status'], 'ACTIVE')
        self.assertEqual(resp_body_network['admin_state_up'], True)
        self.assertEqual(resp_body_network['shared'], False)
        self.assertEqual(resp_body_network['subnets'], ['1', '3', '5'])
        self.assertEqual(resp_body_network['name'], 'Public Network')
        self.assertEqual(resp_body_network['id'], 11)
        self.assertEqual(resp_body_network['tenant_id'], 999999)
        self.assertEqual(resp_body_network['provider:network_type'], 'vlan')
        self.assertEqual(resp_body_network['provider:segmentation_id'], 999)

    def test_on_get_response_networkv2_public(self):
        """Test working path of NetworkV2()"""
        self.net_vlan_mock.getObject.return_value = {'id': 11,
                                                     'name': 'Public Network',
                                                     'subnets': [{'id': 1},
                                                                 {'id': 3},
                                                                 {'id': 5}],
                                                     'vlanNumber': 999}
        self.net_vlan_mock.getNetworkSpace.return_value = 'PUBLIC'
        self.param = 'name'
        self.req.get_param = MagicMock(side_effect=self.side_effect_show)
        self.perform_network_action(11)
        self.check_response_body(self.resp.body['network'])
        self.assertEquals(self.resp.status, 200)
        self.assertEqual(
            self.resp.body['network']['provider:physical_network'], False)

    def test_on_get_response_networkv2_private(self):
        """Test working path of NetworkV2()"""

        self.net_vlan_mock.getObject.return_value = {'id': 11,
                                                     'name': 'Public Network',
                                                     'subnets': [{'id': 1},
                                                                 {'id': 3},
                                                                 {'id': 5}],
                                                     'vlanNumber': 999}
        self.param = 'name'
        self.req.get_param = MagicMock(side_effect=self.side_effect_show)
        self.net_vlan_mock.getNetworkSpace.return_value = 'PRIVATE'
        self.perform_network_action(11)
        self.check_response_body(self.resp.body['network'])
        self.assertEquals(self.resp.status, 200)
        self.assertEqual(
            self.resp.body['network']['provider:physical_network'], True)

    def test_on_get_response_networkv2_invalid_id(self):
        """Test invalid id"""
        self.perform_network_action('BAD_ID')
        self.assertEquals(self.resp.status, 400)


class TestNetworksV2(unittest.TestCase):
    def setUp(self):
        self.req, self.resp = MagicMock(), MagicMock()
        self.account_client_mock = MagicMock()
        self.net_vlan_mock = MagicMock()
        self.req.env = {
            'sl_client': {
                'Account': self.account_client_mock,
                'Network_Vlan': self.net_vlan_mock,
            },
            'auth': {
                'tenant_id': 999999
            },
        }
        self.req.env['sl_client'][
            'Account'].getPublicNetworkVlans.return_value = [{'id': 11},
                                                             {'id': 5555}]

    def side_effect_list(*args):
        if args[1] == 'fields' and args[0].param == 'fields':
            return None

    def side_effect_show(*args):
        if args[1] == 'name' and args[0].param == 'name':
            return '123321'
        else:
            return 'id'

    def perform_networks_action(self):
        """Initaite the NetoworksV2 Instance"""
        instance = NetworksV2()
        instance.on_get(self.req, self.resp)

    def check_response_body(self, resp_body_network):
        self.assertEqual(resp_body_network['status'], 'ACTIVE')
        self.assertEqual(resp_body_network['admin_state_up'], True)
        self.assertEqual(resp_body_network['shared'], False)
        self.assertEqual(resp_body_network['subnets'], ['1', '3', '5'])
        self.assertEqual(resp_body_network['name'], 'Public Network')
        self.assertEqual(resp_body_network['id'], 11)
        self.assertEqual(resp_body_network['tenant_id'], 999999)
        self.assertEqual(resp_body_network['provider:network_type'], 'vlan')
        self.assertEqual(resp_body_network['provider:segmentation_id'], 999)

    def test_on_get_response_networksv2_show(self):
        """Test show function in NetworksV2"""
        self.account_client_mock.getNetworkVlans.return_value = [
            {'id': 123321, 'name': 'Public Network',
             'subnets': [{'id': 1}, {'id': 3}, {'id': 5}], 'vlanNumber': 999}]

        self.param = 'name'
        self.req.get_param = MagicMock(side_effect=self.side_effect_show)
        self.perform_networks_action()
        self.assertEquals(self.resp.status, 200)
        self.assertEqual(self.resp.body['networks'], [{'id': '123321'}])

    def test_on_get_response_networksv2_show_no_match(self):
        """Test show function in NetworksV2 with no matching ID"""
        self.account_client_mock.getNetworkVlans.return_value = []

        self.param = 'name'
        self.req.get_param = MagicMock(side_effect=self.side_effect_show)
        self.perform_networks_action()
        self.assertEquals(self.resp.status, 200)
        self.assertEqual(self.resp.body['networks'], [])

    def test_on_get_response_networksv2_list(self):
        """Test list function"""
        self.account_client_mock.getNetworkVlans.return_value = [
            {'id': 11, 'name': 'Public Network',
             'subnets': [{'id': 1}, {'id': 3}, {'id': 5}], 'vlanNumber': 999}]

        self.param = 'fields'
        self.req.get_param = MagicMock(side_effect=self.side_effect_list)
        self.perform_networks_action()
        self.assertEquals(self.resp.status, 200)
        self.check_response_body(self.resp.body['networks'][0])

    def tearDown(self):
        self.req, self.resp = None, None
        self.account_client_mock, self.net_vlan_mock = None, None
