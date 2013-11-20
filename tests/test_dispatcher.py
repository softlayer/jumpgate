from mock import MagicMock
import unittest

from jumpgate.common.dispatcher import Dispatcher


class TestDispatcher(unittest.TestCase):
    def setUp(self):
        self.app = MagicMock()
        self.disp = Dispatcher(self.app)

    def test_init(self):
        self.assertEquals(self.disp._app, self.app)
        self.assertEquals(self.disp._endpoints, {})

    def test_add_endpoint(self):
        self.disp.add_endpoint('user_page', '/path/to/{tenant_id}')

        self.assertEquals(len(self.disp._endpoints), 1)
        self.assertEquals(self.disp._endpoints['user_page'],
                         ('/path/to/{tenant_id}', None))

    def test_set_handler(self):
        self.disp.add_endpoint('user_page0', '/path0/to/{tenant_id}')
        handler = MagicMock()

        self.disp.set_handler('user_page0', handler)
        self.assertEquals(self.disp._endpoints,
                          {'user_page0': ('/path0/to/{tenant_id}', handler)})

        self.assertRaises(
            ValueError, self.disp.set_handler, 'unknown', handler)

    def test_get_unused_endpoints(self):
        self.disp.add_endpoint('user_page0', '/path0/to/{tenant_id}')
        self.disp.add_endpoint('user_page1', '/path1/to/{tenant_id}')
        self.disp.add_endpoint('user_page2', '/path2/to/{tenant_id}')
        self.disp.set_handler('user_page0', MagicMock())

        unused_endpoints = self.disp.get_unused_endpoints()

        self.assertEquals(unused_endpoints, ['user_page1', 'user_page2'])


class TestDispatcherUrls(unittest.TestCase):
    def setUp(self):
        self.app = MagicMock()
        self.disp = Dispatcher(self.app)

        self.disp.add_endpoint('user_page', '/path/to/{tenant_id}')
        self.disp.add_endpoint('instance_detail',
                               '/path/to/{tenant_id}/{instance_id}')

    def test_get_endpoint_path(self):
        req = MagicMock()
        req.env = {'tenant_id': '1234'}

        path = self.disp.get_endpoint_path(req, 'user_page')

        self.assertEquals(path, '/path/to/1234')

        path = self.disp.get_endpoint_path(
            req, 'instance_detail', instance_id='9876')

        self.assertEquals(path, '/path/to/1234/9876')

    def test_get_endpoint_url(self):
        req = MagicMock()
        req.env = {'tenant_id': '1234'}
        req.protocol = 'http'
        req.get_header.return_value = 'some_host'
        req.app = ''

        path = self.disp.get_endpoint_url(req, 'user_page')

        self.assertEquals(path, 'http://some_host/path/to/1234')

        path = self.disp.get_endpoint_url(
            req, 'instance_detail', instance_id='9876')

        self.assertEquals(path, 'http://some_host/path/to/1234/9876')
