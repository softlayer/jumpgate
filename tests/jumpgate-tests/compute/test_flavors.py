import unittest
import falcon
from falcon.testing import helpers
import mock

from jumpgate.compute.drivers.sl import flavors
from jumpgate.compute.drivers.sl import flavor_list_loader


TENANT_ID = 333333
FLAVOR_LIST = flavor_list_loader.Flavors.get_flavors(app=mock.MagicMock())

def get_client_env(**kwargs):
    env = helpers.create_environ(**kwargs)
    return env


class TestFlavorList(unittest.TestCase):
    '''Unit testing for this class depends on the hard-coded flavors. It will
    require change if the hard-coded flavor list changes. It validates the
    filtering functionality as well as any error checking.
    '''

    def perform_flavor_detail(self, q_str, tenant_id, flavor_list):
        env = get_client_env(query_string=q_str)
        self.req = falcon.Request(env)
        self.resp = falcon.Response()
        self.app = mock.MagicMock()
        instance = flavors.FlavorsDetailV2(app=self.app, flavors=flavor_list)
        instance.on_get(self.req, self.resp, tenant_id)

    def test_on_get_for_flavor_list(self):
        '''Testing the flavor-list without any parameters set for filtering
        '''
        self.perform_flavor_detail('', TENANT_ID, FLAVOR_LIST)
        self.assertEquals(list(self.resp.body.keys()), ['flavors'])
        self.assertEquals(len(self.resp.body['flavors']), 5)

    def test_on_get_for_flavor_list_marker(self):
        '''Testing the flavor-list with the 'marker' parameter set to filter
        some flavors out
        '''
        self.perform_flavor_detail('marker=3', TENANT_ID, FLAVOR_LIST)
        self.assertEquals(len(self.resp.body['flavors']), 2)

    def test_on_get_for_flavor_list_minDisk(self):
        '''Testing the flavor-list with the 'minDisk' parameter set to filter
        some flavors out
        '''
        self.perform_flavor_detail('minDisk=42', TENANT_ID, FLAVOR_LIST)
        self.assertEquals(len(self.resp.body['flavors']), 4)

    def test_on_get_for_flavor_list_minDisk_error(self):
        '''Testing the flavor-list with the 'minDisk' parameter set to invalid
        parameter for error-checking
        '''
        self.perform_flavor_detail('minDisk=random_value',
                                   TENANT_ID, FLAVOR_LIST)
        self.assertEquals(self.resp.status, 400)
        self.assertEquals(self.resp.body['badRequest']['message'],
                          "Invalid minDisk parameter.")

    def test_on_get_for_flavor_list_minRam(self):
        '''Testing the flavor-list with the 'minRam' parameter set to filter
        some flavors out
        '''
        self.perform_flavor_detail('minRam=4096', TENANT_ID, FLAVOR_LIST)
        self.assertEquals(len(self.resp.body['flavors']), 2)

    def test_on_get_for_flavor_list_minRam_error(self):
        '''Testing the flavor-list with the 'minRam' parameter set to invalid
        parameter for error-checking
        '''
        self.perform_flavor_detail('minRam=random_value',
                                   TENANT_ID, FLAVOR_LIST)
        self.assertEquals(self.resp.status, 400)
        self.assertEquals(self.resp.body['badRequest']['message'],
                          "Invalid minRam parameter.")

    def test_on_get_for_flavor_list_limit(self):
        '''Testing the flavor-list with the 'limit' parameter set to filter
        some flavors out
        '''
        self.perform_flavor_detail('limit=2', TENANT_ID, FLAVOR_LIST)
        self.assertEquals(len(self.resp.body['flavors']), 2)

    def test_on_get_for_flavor_list_limit_error(self):
        '''Testing the flavor-list with the 'limit' parameter set to invalid
        parameter for error-checking
        '''
        self.perform_flavor_detail('limit=random_value',
                                   TENANT_ID, FLAVOR_LIST)
        self.assertEquals(self.resp.status, 400)
        self.assertEquals(self.resp.body['badRequest']['message'],
                          "Invalid limit parameter.")

    def test_on_get_invalid_json_string_flavor_list(self):
        '''Testing that the default hard-coded flavor list is used, when the
        json string provided in the config file is not formatted correctly
        '''
        self.perform_flavor_detail('', TENANT_ID, FLAVOR_LIST)
        self.assertEquals(list(self.resp.body.keys()), ['flavors'])
        self.assertEquals(len(self.resp.body['flavors']), 5)

    def format_flavors(self, flavors):
        flavors = {int(key): flavor_list_loader.format_flavor_extra_specs(val)
                   for key, val in flavors.items()}
        return flavor_list_loader.get_listing_flavors(flavors)

    def test_on_get_flavor_list_missing_id(self):
        '''Testing that a flavor is ignored when it is missing a required
        parameter (flavor 2 is missing the 'id' parameter)
        and is not formatted correctly
        '''
        test_dict = {"1": {"disk-type": "SAN",
                           "name": "1 vCPU, 1GB ram, 25GB, SAN",
                           "ram": 1024, "cpus": 1, "disk": 25,
                           "id": "1"},
                     "2" : {"disk-type": "SAN",
                            "name": "1 vCPU, 1GB ram, 100GB, SAN",
                            "ram": 1024, "cpus": 1, "disk": 100}}
        self.perform_flavor_detail('', TENANT_ID,
                                   self.format_flavors(test_dict))
        self.assertEquals(list(self.resp.body.keys()), ['flavors'])
        self.assertEquals(len(self.resp.body['flavors']), 1)

    def test_on_get_flavor_list_missing_cpus(self):
        '''Testing that a flavor is ignored when it is missing a required
        parameter (flavor 2 is missing the 'cpus' parameter)
        and is not formatted correctly
        '''
        test_dict = {"1": {"disk-type": "SAN",
                                       "name": "1 vCPU, 1GB ram, 25GB, SAN",
                                       "ram": 1024, "cpus": 1, "disk": 25,
                                       "id": "1"},
                                 "2": {"disk-type": "SAN",
                                       "name": "1 vCPU, 1GB ram, 100GB, SAN",
                                       "ram": 1024, "disk": 100, "id": "2"}}
        self.perform_flavor_detail('', TENANT_ID,
                                   self.format_flavors(test_dict))
        self.assertEquals(list(self.resp.body.keys()), ['flavors'])
        self.assertEquals(len(self.resp.body['flavors']), 1)

    def test_on_get_flavor_list_missing_name(self):
        '''Testing that a flavor is ignored when it is missing a required
        parameter (flavor 2 is missing the 'name' parameter)
        and is not formatted correctly
        '''
        test_dict = {"1": {"disk-type": "SAN",
                                       "name": "1 vCPU, 1GB ram, 25GB, SAN",
                                       "ram": 1024, "cpus": 1, "disk": 25,
                                       "id": "1"},
                                 "2": {"disk-type": "Local", "ram": 1024,
                                       "cpus": 1, "disk": 100, "id": "2"}}
        self.perform_flavor_detail('', TENANT_ID,
                                   self.format_flavors(test_dict))
        self.assertEquals(list(self.resp.body.keys()), ['flavors'])
        self.assertEquals(len(self.resp.body['flavors']), 1)

    def test_on_get_flavor_list_missing_ram(self):
        '''Testing that a flavor is ignored when it is missing a required
        parameter (flavor 2 is missing the 'ram' parameter)
        and is not formatted correctly
        '''
        test_dict = {"1": {"disk-type": "SAN",
                                       "name": "1 vCPU, 1GB ram, 25GB, SAN",
                                       "ram": 1024, "cpus": 1, "disk": 25,
                                       "id": "1"},
                                 "2": {"disk-type": "SAN",
                                       "name": "1 vCPU, 1GB ram, 100GB, SAN",
                                       "cpus": 1, "disk": 100, "id": "2"}}
        self.perform_flavor_detail('', TENANT_ID,
                                   self.format_flavors(test_dict))
        self.assertEquals(list(self.resp.body.keys()), ['flavors'])
        self.assertEquals(len(self.resp.body['flavors']), 1)

    def test_on_get_flavor_list_missing_disk(self):
        '''Testing that a flavor is ignored when it is missing a required
        parameter (flavor 2 is missing the 'disk' parameter)
        and is not formatted correctly
        '''
        test_dict = {"1": {"disk-type": "SAN",
                                       "name": "1 vCPU, 1GB ram, 25GB, SAN",
                                       "ram": 1024, "cpus": 1, "disk": 25,
                                       "id": "1"},
                                 "2": {"disk-type": "SAN",
                                       "name": "1 vCPU, 1GB ram, 100GB, SAN",
                                       "ram": 1024, "cpus": 1, "id": "2"}}
        self.perform_flavor_detail('', TENANT_ID,
                                   self.format_flavors(test_dict))
        self.assertEquals(list(self.resp.body.keys()), ['flavors'])
        self.assertEquals(len(self.resp.body['flavors']), 1)

    def test_on_get_flavor_list_duplicate_flavors(self):
        '''Testing that a flavor is ignored when another flavor with the
        same flavor id is already used
        '''
        flavor_list_loader.Flavors._flavors = None
        test_dict = {"1": {"disk-type": "SAN",
                                       "name": "1 vCPU, 1GB ram, 25GB, SAN",
                                       "ram": 1024, "cpus": 1, "disk": 25,
                                       "id": "1"},
                                 "2": {"disk-type": "SAN",
                                       "name": "1 vCPU, 1GB ram, 100GB, SAN",
                                       "ram": 1024, "cpus": 1, "disk": 100,
                                       "id": "2"},
                                 "3": {"disk-type": "SAN",
                                       "name": "1 vCPU, 2GB ram, 100GB, SAN",
                                       "ram": 2048, "cpus": 1, "disk": 100,
                                       "id": "1"}}
        self.perform_flavor_detail('', TENANT_ID,
                                   self.format_flavors(test_dict))
        self.assertEquals(list(self.resp.body.keys()), ['flavors'])
        self.assertEquals(len(self.resp.body['flavors']), 2)

    def test_on_get_flavor_list_duplicate_flavors_invalid(self):
        '''Testing that a flavor is ignored when it is not formatted
        correctly and that a second flavor with the same flavor id formatted
        correctly is used
        '''
        test_dict = {"1": {"disk-type": "SAN",
                                       "name": "1 vCPU, 1GB ram, 25GB, SAN",
                                       "ram": 1024, "cpus": 1, "id": "1"},
                                 "2": {"disk-type": "SAN",
                                       "name": "1 vCPU, 1GB ram, 100GB, SAN",
                                       "ram": 1024, "cpus": 1, "disk": 100,
                                       "id": "2"},
                                 "3": {"disk-type": "SAN",
                                       "name": "1 vCPU, 2GB ram, 100GB, SAN",
                                       "ram": 2048, "cpus": 1, "disk": 100,
                                       "id": "1"}}
        self.perform_flavor_detail('', TENANT_ID,
                                   self.format_flavors(test_dict))
        self.assertEquals(list(self.resp.body.keys()), ['flavors'])
        self.assertEquals(len(self.resp.body['flavors']), 2)

    def tearDown(self):
        flavor_list_loader.Flavors._flavors = None
