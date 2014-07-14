import unittest

import falcon
from falcon.testing import helpers
import mock

from jumpgate.network.drivers.sl import subnets

SUBNET_DICT = {'id': 10,
               'networkIdentifier': '9.0.3.192',
               'tenant_id': '6',
               'cidr': 28,
               'networkVlanId': 5,
               'gateway': '9.0.3.193',
               'version': 4,
               'name': 'name'}


def get_client_env(**kwargs):
    client = mock.MagicMock()
    env = helpers.create_environ(**kwargs)
    env['sl_client'] = client
    env['auth'] = {'tenant_id': 999999}
    return client, env


class TestSubnetV2(unittest.TestCase):

    def check_body_response(self, body_subnet):
        self.assertEqual(body_subnet['id'], '10')
        self.assertEqual(body_subnet['name'], '')
        self.assertEqual(body_subnet['enable_dhcp'], False)
        self.assertEqual(body_subnet['gateway_ip'], '9.0.3.193')
        self.assertEqual(body_subnet['ip_version'], 4)
        self.assertEqual(body_subnet['tenant_id'], 999999)
        self.assertEqual(body_subnet['cidr'], '9.0.3.192/28')
        self.assertEqual(body_subnet['allocation_pools'],
                         [{'start': '9.0.3.194', 'end': '9.0.3.206'}])
        self.assertEqual(body_subnet['network_id'], 5)
        self.assertEqual(body_subnet['dns_nameservers'], [])
        self.assertEqual(body_subnet['host_routes'], [])

    def test_on_get_response_subnetv2(self):
        """Test working path of SubnetV2()"""
        client, env = get_client_env(query_string='name=10')

        SUBNET_DICT['id'] = 10
        client['Network_Subnet'].getObject.return_value = SUBNET_DICT
        req = falcon.Request(env)
        resp = falcon.Response()

        subnets.SubnetV2().on_get(req, resp, 10)
        self.assertEquals(resp.status, 200)
        self.check_body_response(resp.body['subnet'])

    def test_on_get_response_subnetv2_invalid_id(self):
        """Test invalid id"""
        client, env = get_client_env()
        req = falcon.Request(env)
        resp = falcon.Response()

        subnets.SubnetV2().on_get(req, resp, 'BAD_ID')
        self.assertEquals(resp.status, 400)


class TestSubnetsV2(unittest.TestCase):

    def check_body_response(self, body_subnet):
        self.assertEqual(body_subnet['id'], '10')
        self.assertEqual(body_subnet['name'], '')
        self.assertEqual(body_subnet['enable_dhcp'], False)
        self.assertEqual(body_subnet['gateway_ip'], '9.0.3.193')
        self.assertEqual(body_subnet['ip_version'], 4)
        self.assertEqual(body_subnet['tenant_id'], 999999)
        self.assertEqual(body_subnet['cidr'], '9.0.3.192/28')
        self.assertEqual(body_subnet['allocation_pools'],
                         [{'start': '9.0.3.194', 'end': '9.0.3.206'}])
        self.assertEqual(body_subnet['network_id'], 5)
        self.assertEqual(body_subnet['dns_nameservers'], [])
        self.assertEqual(body_subnet['host_routes'], [])

    def test_on_get_response_subnetsv2_show(self):
        """Test show function in SubnetsV2"""
        client, env = get_client_env()

        SUBNET_DICT['id'] = 10
        client['Account'].getSubnets.return_value = [SUBNET_DICT]
        req = falcon.Request(env)
        resp = falcon.Response()

        subnets.SubnetsV2().on_get(req, resp)
        self.assertEquals(resp.status, 200)
        self.check_body_response(resp.body['subnets'][0])

    def test_on_get_response_subnetsv2_show_no_match(self):
        """Test show function in SubnetsV2 with no matching ID"""
        client, env = get_client_env(query_string='name=10')
        SUBNET_DICT['id'] = 9
        client['Account'].getSubnets.return_value = []
        req = falcon.Request(env)
        resp = falcon.Response()

        subnets.SubnetsV2().on_get(req, resp)
        self.assertEquals(resp.status, 200)
        self.assertEqual(resp.body['subnets'], [])

    def test_on_get_subnetsv2_response_list(self):
        """Test list function"""
        client, env = get_client_env(query_string='name=10')
        SUBNET_DICT['id'] = 10
        client['Account'].getSubnets.return_value = [SUBNET_DICT]
        req = falcon.Request(env)
        resp = falcon.Response()

        subnets.SubnetsV2().on_get(req, resp)
        self.check_body_response(resp.body['subnets'][0])
