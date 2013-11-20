import unittest
from mock import MagicMock

from jumpgate.api import Jumpgate
from jumpgate.common.hooks import hook_format, hook_set_uuid, hook_log_request
from jumpgate.common.dispatcher import Dispatcher

import falcon


class StubResource(object):
    pass


class TestJumpgateInit(unittest.TestCase):
    def test_init(self):
        config = MagicMock()
        app = Jumpgate(config)

        self.assertEqual(app.config, config)
        self.assertEqual(app.installed_modules, {})

        self.assertIsInstance(app.before_hooks, list)
        self.assertIsInstance(app.after_hooks, list)
        self.assertEqual(app.before_hooks, [hook_set_uuid])
        self.assertEqual(app.after_hooks, [hook_format, hook_log_request])

        self.assertEqual(app._routes, [])
        self.assertEqual(app._dispatchers, {})


class TestJumpgate(unittest.TestCase):
    def setUp(self):
        self.config = MagicMock()
        self.app = Jumpgate(self.config)

    def test_add_single_route(self):
        resource = MagicMock()
        self.app.add_route('/this/is/a/{test}', resource)

        self.assertEqual(self.app._routes, [('/this/is/a/{test}', resource)])

    def test_route_order(self):
        resources = [MagicMock() for i in range(10)]
        for i, resource in enumerate(resources):
            self.app.add_route('/this/is/a/test/{%s}' % i, resource)

        self.assertEqual(len(self.app._routes), 10)
        for i, resource in enumerate(resources):
            self.assertEqual(self.app._routes[i],
                             ('/this/is/a/test/{%s}' % i, resource))

    def test_make_api(self):
        resources = [StubResource() for i in range(10)]
        for i, resource in enumerate(resources):
            self.app.add_route('/this/is/a/test/{%s}' % i, resource)

        api = self.app.make_api()
        self.assertTrue(hasattr(api, '__call__'))
        self.assertIsInstance(api, falcon.API)
        self.assertEqual(len(api._routes), 10)

    def test_add_get_dispatcher(self):
        disp = Dispatcher(self.app)
        self.app.add_dispatcher('SERVICE', disp)

        self.assertEqual(self.app._dispatchers, {'SERVICE': disp})
