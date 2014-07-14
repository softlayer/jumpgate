import unittest

import falcon
from falcon.testing import helpers
import mock

from jumpgate.network.drivers.sl import networks


def get_client_env(**kwargs):
    client = mock.MagicMock()
    env = helpers.create_environ(**kwargs)
    env['sl_client'] = client
    env['auth'] = {'tenant_id': 999999}
    return client, env


class TestNetworkV2(unittest.TestCase):

    def check_response_body(self, resp_body_network):
        self.assertEqual(resp_body_network['status'], 'ACTIVE')
        self.assertEqual(resp_body_network['admin_state_up'], True)
        self.assertEqual(resp_body_network['shared'], False)
        self.assertEqual(resp_body_network['subnets'], ['1', '3', '5'])
        self.assertEqual(resp_body_network['name'], 'Public Network')
        self.assertEqual(resp_body_network['id'], '11')
        self.assertEqual(resp_body_network['tenant_id'], 999999)
        self.assertEqual(resp_body_network['provider:network_type'], 'vlan')
        self.assertEqual(resp_body_network['provider:segmentation_id'], 999)

    def test_on_get_response_networkv2_public(self):
        """Test working path of NetworkV2()"""
        client, env = get_client_env(query_string='name=123321')

        net_vlan = client['Network_Vlan']
        net_vlan.getObject.return_value = {'id': 11,
                                           'name': 'Public Network',
                                           'subnets': [{'id': 1},
                                                       {'id': 3},
                                                       {'id': 5}],
                                           'vlanNumber': 999,
                                           'networkSpace': 'PUBLIC'}
        req = falcon.Request(env)
        resp = falcon.Response()

        networks.NetworkV2().on_get(req, resp, 11)
        self.check_response_body(resp.body['network'])
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.body['network']['provider:physical_network'],
                         False)

    def test_on_get_response_networkv2_private(self):
        """Test working path of NetworkV2()"""

        client, env = get_client_env(query_string='name=123321')
        net_vlan = client['Network_Vlan']
        net_vlan.getObject.return_value = {'id': 11,
                                           'name': 'Public Network',
                                           'subnets': [{'id': 1},
                                                       {'id': 3},
                                                       {'id': 5}],
                                           'vlanNumber': 999,
                                           'networkSpace': 'PRIVATE'}
        req = falcon.Request(env)
        resp = falcon.Response()

        networks.NetworkV2().on_get(req, resp, 11)

        self.check_response_body(resp.body['network'])
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.body['network']['provider:physical_network'],
                         True)

    def test_on_get_response_networkv2_invalid_id(self):
        """Test invalid id"""
        client, env = get_client_env()

        req = falcon.Request(env)
        resp = falcon.Response()

        networks.NetworkV2().on_get(req, resp, 'BAD_ID')
        self.assertEqual(resp.status, 400)


class TestNetworksV2(unittest.TestCase):

    def check_response_body(self, resp_body_network):
        self.assertEqual(resp_body_network['status'], 'ACTIVE')
        self.assertEqual(resp_body_network['admin_state_up'], True)
        self.assertEqual(resp_body_network['shared'], False)
        self.assertEqual(resp_body_network['subnets'], ['1', '3', '5'])
        self.assertEqual(resp_body_network['name'], 'Public Network')
        self.assertEqual(resp_body_network['id'], '123321')
        self.assertEqual(resp_body_network['tenant_id'], 999999)
        self.assertEqual(resp_body_network['provider:network_type'], 'vlan')
        self.assertEqual(resp_body_network['provider:segmentation_id'], 999)

    def test_on_get_response_networksv2_show(self):
        """Test show function in NetworksV2"""

        client, env = get_client_env(query_string='name=123321')
        account = client['Account']
        account.getNetworkVlans.return_value = [
            {'id': 123321,
             'name': 'Public Network',
             'subnets': [{'id': 1}, {'id': 3}, {'id': 5}],
             'vlanNumber': 999,
             'networkSpace': 'PRIVATE'}]

        req = falcon.Request(env)
        resp = falcon.Response()

        networks.NetworksV2().on_get(req, resp)
        self.assertEqual(resp.status, 200)
        self.check_response_body(resp.body['networks'][0])

    def test_on_get_response_networksv2_show_no_match(self):
        """Test show function in NetworksV2 with no matching ID"""

        client, env = get_client_env(query_string='name=123321')
        client['Account'].getNetworkVlans.return_value = []

        req = falcon.Request(env)
        resp = falcon.Response()

        networks.NetworksV2().on_get(req, resp)
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.body['networks'], [])

    def test_on_get_response_networksv2_list(self):
        """Test list function"""

        client, env = get_client_env(query_string='name=123321')
        client['Account'].getNetworkVlans.return_value = [
            {'id': '123321',
             'name': 'Public Network',
             'subnets': [{'id': 1}, {'id': 3}, {'id': 5}],
             'vlanNumber': 999,
             'networkSpace': 'PRIVATE'}]

        req = falcon.Request(env)
        resp = falcon.Response()

        networks.NetworksV2().on_get(req, resp)
        self.assertEqual(resp.status, 200)
        self.check_response_body(resp.body['networks'][0])
