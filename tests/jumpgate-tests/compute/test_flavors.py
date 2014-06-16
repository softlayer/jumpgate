from mock import MagicMock
from jumpgate.compute.drivers.sl.flavors import FlavorsDetailV2
import unittest

TENANT_ID = 333333


class TestFlavorList(unittest.TestCase):
    '''Unit testing for this class depends on the hard-coded flavors. It will
    require change if the hard-coded flavor list changes. It validates the
    filtering functionality as well as any error checking. '''

    def test_init(self):
        app = MagicMock()
        instance = FlavorsDetailV2(app)
        self.assertEqual(app, instance.app)

    def setUp(self):
        self.req, self.resp = MagicMock(), MagicMock()

    def side_effect(*args):
        if (args[1] == 'marker' and args[0].param == 'marker'):
            return '3'
        elif (args[1] == 'minDisk' and args[0].param == 'minDisk'):
            return 42
        elif (args[1] == 'minRam' and args[0].param == 'minRam'):
            return 4 * 1024
        elif (args[1] == 'limit' and args[0].param == 'limit'):
            return 7
        return None

    def side_effect_error(*args):
        if ((args[1] == 'minDisk' and args[0].param == 'minDisk') or
                (args[1] == 'minRam' and args[0].param == 'minRam') or
                (args[1] == 'limit' and args[0].param == 'limit')):
            return 'random_value'
        return None

    def perform_flavor_list(self, tenant_id, flag):
        instance = FlavorsDetailV2(app=MagicMock())
        if flag:
            self.req.get_param = MagicMock(side_effect=self.side_effect)
        else:
            self.req.get_param = MagicMock(side_effect=self.side_effect_error)
        instance.on_get(self.req, self.resp, tenant_id)

    def test_on_get_for_flavor_list(self):
        '''Testing the flavor-list without any parameters set for filtering'''
        self.param = 'no_params'
        self.perform_flavor_list(TENANT_ID, 1)
        # For python 3.3/3.4 dict.keys() returns iterable views instead of
        # list.
        self.assertEquals(list(self.resp.body.keys()), ['flavors'])
        self.assertEquals(len(self.resp.body['flavors']), 10)

    def test_on_get_for_flavor_list_marker(self):
        '''Testing the flavor-list with the 'marker' parameter set to filter
        some flavors out'''
        self.param = 'marker'
        self.perform_flavor_list(TENANT_ID, 1)
        self.assertEquals(len(self.resp.body['flavors']), 2)

    def test_on_get_for_flavor_list_minDisk(self):
        '''Testing the flavor-list with the 'minDisk' parameter set to filter
        some flavors out'''
        self.param = 'minDisk'
        self.perform_flavor_list(TENANT_ID, 1)
        self.assertEquals(len(self.resp.body['flavors']), 8)

    def test_on_get_for_flavor_list_minDisk_error(self):
        '''Testing the flavor-list with the 'minDisk' parameter set to invalid
        parameter for error-checking'''
        self.param = 'minDisk'
        self.perform_flavor_list(TENANT_ID, 0)
        self.assertEquals(self.resp.status, 400)
        self.assertEquals(self.resp.body['badRequest']['message'],
                          "Invalid minDisk parameter.")

    def test_on_get_for_flavor_list_minRam(self):
        '''Testing the flavor-list with the 'minRam' parameter set to filter
        some flavors out'''
        self.param = 'minRam'
        self.perform_flavor_list(TENANT_ID, 1)
        self.assertEquals(len(self.resp.body['flavors']), 4)

    def test_on_get_for_flavor_list_minRam_error(self):
        '''Testing the flavor-list with the 'minRam' parameter set to invalid
        parameter for error-checking'''
        self.param = 'minRam'
        self.perform_flavor_list(TENANT_ID, 0)
        self.assertEquals(self.resp.status, 400)
        self.assertEquals(self.resp.body['badRequest']['message'],
                          "Invalid minRam parameter.")

    def test_on_get_for_flavor_list_limit(self):
        '''Testing the flavor-list with the 'limit' parameter set to filter
        some flavors out'''
        self.param = 'limit'
        self.perform_flavor_list(TENANT_ID, 1)
        self.assertEquals(len(self.resp.body['flavors']), 7)

    def test_on_get_for_flavor_list_limit_error(self):
        '''Testing the flavor-list with the 'limit' parameter set to invalid
        parameter for error-checking'''
        self.param = 'limit'
        self.perform_flavor_list(TENANT_ID, 0)
        self.assertEquals(self.resp.status, 400)
        self.assertEquals(self.resp.body['badRequest']['message'],
                          "Invalid limit parameter.")

    def tearDown(self):
        self.req, self.resp, self.app = None, None, None
