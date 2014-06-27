import unittest

from mock import MagicMock
from jumpgate.network.drivers.sl.subnets import SubnetV2, SubnetsV2

SUBNET_DICT = {'id': 10, 'networkIdentifier': '9.0.3.192',
               'tenant_id': '6', 'cidr': 28, 'networkVlanId': 5,
               'gateway': '9.0.3.193', 'version': 4, 'name': 'name'}


class TestSubnetV2(unittest.TestCase):
    def setUp(self):
        self.req, self.resp = MagicMock(), MagicMock()
        self.account_client_mock = MagicMock()
        self.network_subnet_mock = MagicMock()
        self.req.env = {
            'sl_client': {
                'Account': self.account_client_mock,
                'Network_Subnet': self.network_subnet_mock
            },
            'auth': {
                'tenant_id': 999999
            }
        }

    def side_effect_show(*args):
        if args[1] == 'name' and args[0].param == 'name':
            return '10'
        else:
            return None


    def perform_subnetv2_action(self, subnet_id):
        """Initiate the SubnetV2 Instant with a given subnet id"""
        instance = SubnetV2()
        instance.on_get(self.req, self.resp, subnet_id)

    def check_body_response(self, body_subnet):
        self.assertEqual(body_subnet['id'], 10)
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
        SUBNET_DICT['id'] = 10
        self.network_subnet_mock.getObject.return_value = SUBNET_DICT
        self.param = 'name'
        self.req.get_param = MagicMock(side_effect=self.side_effect_show)
        self.perform_subnetv2_action(10)
        self.assertEquals(self.resp.status, 200)
        self.check_body_response(self.resp.body['subnet'])

    def test_on_get_response_subnetv2_invalid_id(self):
        """Test invalid id"""
        self.perform_subnetv2_action('BAD_ID')
        self.assertEquals(self.resp.status, 400)

    def tearDown(self):
        self.req, self.resp = None, None
        self.account_client_mock, self.network_subnet_mock = None, None


class TestSubnetsV2(unittest.TestCase):
    def setUp(self):
        self.req, self.resp = MagicMock(), MagicMock()
        self.account_client_mock = MagicMock()
        self.network_subnet_mock = MagicMock()
        self.req.env = {
            'sl_client': {
                'Account': self.account_client_mock,
                'Network_Subnet': self.network_subnet_mock
            },
            'auth': {
                'tenant_id': 999999
            }
        }

    def side_effect_list(*args):
        if args[1] == 'fields' and args[0].param == 'fields':
            return None

    def side_effect_show(*args):
        if args[1] == 'name' and args[0].param == 'name':
            return '10'
        else:
            return None

    def perform_subnetsv2_action(self):
        """Initaite the SubnetsV2 Instance"""
        instance = SubnetsV2()
        instance.on_get(self.req, self.resp)

    def check_body_response(self, body_subnet):
        self.assertEqual(body_subnet['id'], 10)
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
        SUBNET_DICT['id'] = 10
        self.account_client_mock.getSubnets.return_value = [SUBNET_DICT]

        self.param = 'name'
        self.req.get_param = MagicMock(side_effect=self.side_effect_show)
        self.perform_subnetsv2_action()
        self.assertEquals(self.resp.status, 200)
        self.assertEquals(self.resp.body['subnets'], [{'id': '10'}])

    def test_on_get_response_subnetsv2_show_no_match(self):
        """Test show function in SubnetsV2 with no matching ID"""
        SUBNET_DICT['id'] = 9
        self.account_client_mock.getSubnets.return_value = []
        self.param = 'name'
        self.req.get_param = MagicMock(side_effect=self.side_effect_show)
        self.perform_subnetsv2_action()
        self.assertEquals(self.resp.status, 200)
        self.assertEqual(self.resp.body['subnets'], [])

    def test_on_get_subnetsv2_response_list(self):
        """Test list function"""
        SUBNET_DICT['id'] = 10
        self.account_client_mock.getSubnets.return_value = [SUBNET_DICT]
        self.param = 'fields'
        self.req.get_param = MagicMock(side_effect=self.side_effect_list)
        self.perform_subnetsv2_action()
        self.check_body_response(self.resp.body['subnets'][0])

    def tearDown(self):
        self.req, self.resp = None, None
        self.account_client_mock, self.network_subnet_mock = None, None
