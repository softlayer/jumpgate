import unittest
from mock import MagicMock, call, patch

from jumpgate.api import Jumpgate, make_api
from jumpgate.common.hooks import hook_format, hook_set_uuid, hook_log_request
from jumpgate.common.dispatcher import Dispatcher
from jumpgate.common.nyi import NYI

import falcon


class StubResource(object):
    pass


TEST_CFG = {
    'compute': {'driver': 'path.to.compute.driver',
                'mount': '/compute'},
    'identity': {'driver': 'path.to.identity.driver', 'mount': None},
    'enabled_services': ['compute', 'identity']
}


class TestJumpgateInit(unittest.TestCase):
    def test_init(self):
        app = Jumpgate()

        self.assertEqual(app.installed_modules, {})

        self.assertIsInstance(app.before_hooks, list)
        self.assertIsInstance(app.after_hooks, list)
        self.assertEqual(app.before_hooks, [hook_set_uuid])
        self.assertEqual(app.after_hooks, [hook_format, hook_log_request])

        self.assertEqual(app._dispatchers, {})


class TestJumpgate(unittest.TestCase):
    def setUp(self):
        self.config = MagicMock()
        self.app = Jumpgate()

    def test_make_api(self):
        # Populate a dispatcher with some resources
        disp = Dispatcher()
        resources = [StubResource() for i in range(10)]
        for i, resource in enumerate(resources):
            disp.add_endpoint('test_%s' % i, '/path/to/%s' % i)
            disp.set_handler('test_%s' % i, resource)

        self.app.add_dispatcher('SERVICE', disp)

        api = self.app.make_api()
        self.assertTrue(hasattr(api, '__call__'))
        self.assertIsInstance(api, falcon.API)
        self.assertEqual(len(api._routes), 10)

        # Make sure the default route is set correctly
        nyi = NYI()
        route_map, _ = api._default_route
        for verb, handler in route_map.items():
            self.assertEqual(handler.__name__,
                             getattr(nyi, 'on_' + verb.lower()).__name__)

    def test_add_get_dispatcher(self):
        disp = Dispatcher()
        self.app.add_dispatcher('SERVICE', disp)

        self.assertEqual(self.app._dispatchers, {'SERVICE': disp})

        disp_return = self.app.get_dispatcher('SERVICE')
        self.assertEqual(disp_return, disp)

    def test_get_endpoint_url(self):
        disp = Dispatcher()
        disp.add_endpoint('user_page0', '/path0/to/{tenant_id}')
        self.app.add_dispatcher('SERVICE', disp)

        req = MagicMock()
        req.env = {'tenant_id': '1234'}
        req.protocol = 'http'
        req.get_header.return_value = 'some_host'
        req.app = ''

        url = self.app.get_endpoint_url('SERVICE', req, 'user_page0')
        self.assertEqual(url, 'http://some_host/path0/to/1234')

    @patch('jumpgate.api.importlib.import_module')
    def test_load_drivers(self, import_module):
        compute_disp = MagicMock()
        identity_disp = MagicMock()
        self.app._dispatchers = {'compute': compute_disp,
                                 'identity': identity_disp}

        with patch('jumpgate.api.CONF', TEST_CFG):
            self.app.load_drivers()

            import_module.assert_has_calls([
                call('path.to.compute.driver'),
                call().setup_routes(self.app, compute_disp),
                call('path.to.identity.driver'),
                call().setup_routes(self.app, identity_disp),
            ])

    def test_load_endpoints(self):
        with patch('jumpgate.api.CONF', TEST_CFG):
            self.app.load_endpoints()

        self.assertEquals(len(self.app._dispatchers), 2)
        self.assertEquals(list(self.app._dispatchers.keys()),
                          ['compute', 'identity'])

        self.assertEquals(self.app.installed_modules,
                          {'baremetal': False,
                           'compute': True,
                           'identity': True,
                           'image': False,
                           'network': False,
                           'volume': False})


class TestMakeAPI(unittest.TestCase):
    @patch('jumpgate.api.Jumpgate.load_drivers')
    def test_make_api(self, load_drivers):
        api = make_api()

        self.assertTrue(hasattr(api, '__call__'))
        self.assertIsInstance(api, falcon.API)
