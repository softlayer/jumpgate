import unittest
import falcon
from falcon.testing import helpers
import mock

from jumpgate.compute.drivers.sl import extra_specs


TENANT_ID = 333333


def get_client_env(**kwargs):
    env = helpers.create_environ(**kwargs)
    return env


class TestExtraSpecsFlavor(unittest.TestCase):
    '''Checks that all the optional parameters are sent in the response
    and also error-checking for invalid flavor id
    '''

    def perform_extra_detail(self, tenant_id, flavor_id):
        env = get_client_env()
        self.req = falcon.Request(env)
        self.resp = falcon.Response()
        instance = extra_specs.ExtraSpecsFlavorV2(app=mock.MagicMock())
        instance.on_get(self.req, self.resp, tenant_id, flavor_id)

    def test_on_get_for_all_details(self):
        '''Testing on a valid flavor_id
        '''
        self.perform_extra_detail(TENANT_ID, 1)
        self.assertEquals(list(self.resp.body.keys()), ['extra_specs'])
        self.assertEquals(len(self.resp.body['extra_specs']), 1)
        '''Checks that the 1 optional parameter (portspeed) is being sent in
        response, and that no other parameter is in extra-specs
        '''
        self.assertEquals('portspeed' in self.resp.body['extra_specs'], True)
        self.assertEquals('swap' in self.resp.body['extra_specs'], False)
        self.assertEquals('disk-type' in
                          self.resp.body['extra_specs'], False)
        self.assertEquals('rxtx_factor' in self.resp.body['extra_specs'],
                          False)
        self.assertEquals(self.resp.status, 200)

    def test_on_get_for_out_of_range_flavor(self):
        '''Testing on an out of range flavor_id
        '''
        self.perform_extra_detail(TENANT_ID, 23)
        self.assertEquals(self.resp.status, 400)

    def test_on_get_for_invalid_flavor(self):
        '''Testing on an invalid (not an number) flavor_id
        '''
        self.perform_extra_detail(TENANT_ID, 'not a number')
        self.assertEquals(self.resp.status, 400)


class TestExtraSpecsFlavorKey(unittest.TestCase):
    '''Checks that the appropriate optional parameter is sent when requested
    and also error-checking for invalid flavor id and invalid key id
    '''

    def perform_extra_detail_key(self, tenant_id, flavor_id, key_id):
        env = get_client_env()
        self.req = falcon.Request(env)
        self.resp = falcon.Response()
        instance = extra_specs.ExtraSpecsFlavorKeyV2(app=mock.MagicMock())
        instance.on_get(self.req, self.resp, tenant_id, flavor_id, key_id)

    def test_on_get_for_portspeed(self):
        '''Testing for the 'portspeed' optional spec
        '''
        self.perform_extra_detail_key(TENANT_ID, 1, 'portspeed')
        self.assertEquals(list(self.resp.body.keys()), ['portspeed'])
        self.assertEquals(self.resp.status, 200)

    def test_on_get_for_invalid_flavor(self):
        '''Testing for an invalid flavor id
        '''
        self.perform_extra_detail_key(TENANT_ID, 42, 'portspeed')
        self.assertEquals(self.resp.status, 400)

    def test_on_get_for_invalid_key(self):
        '''Testing for a valid flavor id, but invalid key (optional spec)
        '''
        self.perform_extra_detail_key(TENANT_ID, 1, 'invalid_key')
        self.assertEquals(self.resp.status, 400)
