from mock import MagicMock, patch
import unittest

import six

from jumpgate.common.openstack import setup_responder, OpenStackResponder


def make_response(status_code=200, body=None, content_type='application/json'):
    resp = MagicMock()
    resp.status_code = status_code
    resp.content_type = content_type

    headers = {'Content-Type': content_type}
    if body:
        headers['Content-Length'] = '10'
        resp.raw = six.StringIO(body)
    else:
        headers['Content-Length'] = '0'
        resp.raw = six.StringIO()

    resp.headers = headers
    return resp


class TestSetupResponder(unittest.TestCase):
    def test_setup_responder(self):
        app = MagicMock()
        disp = MagicMock()
        disp.get_unused_endpoints.return_value = ['endpoint0',
                                                  'endpoint1',
                                                  'endpoint2']
        setup_responder(app, disp, 'compute')
        print(app.mock_calls)
        handler_calls = disp.set_handler.mock_calls
        self.assertEquals(len(handler_calls), 3)
        for i, (_, args, _) in enumerate(handler_calls):
            self.assertEquals(args[0], 'endpoint%s' % i)
            self.assertIsInstance(args[1], OpenStackResponder)


class TestOpenstackResponder(unittest.TestCase):
    def test_init(self):
        responder = OpenStackResponder('/mount-point',
                                       'http://127.0.0.1:1234/v2')

        self.assertEquals(responder.mount, '/mount-point')
        self.assertEquals(responder.endpoint, 'http://127.0.0.1:1234/v2')

    @patch('jumpgate.common.openstack.requests.request')
    def test_standard_responder_get(self, request):
        request.return_value = make_response()
        responder = OpenStackResponder(None, 'http://127.0.0.1:1234/v2')
        req, resp = MagicMock(), MagicMock()
        req.method = 'GET'
        req.relative_uri = '/path/to/resource'
        responder.on_get(req, resp)

        request.assert_called_with(
            req.method,
            'http://127.0.0.1:1234/v2/path/to/resource',
            data=None,
            headers=req.headers,
            stream=True)

        self.assertEquals(resp.status, 200)
        self.assertEquals(resp.content_type, 'application/json')
        self.assertEquals(resp.stream_len, '0')
        resp.set_headers.assert_called_with({})
        self.assertEquals(resp.stream.read(), '')

    @patch('jumpgate.common.openstack.requests.request')
    def test_standard_responder_post(self, request):
        request.return_value = make_response(body='TEST BODY')
        responder = OpenStackResponder(None, 'http://127.0.0.1:1234/v2')
        req, resp = MagicMock(), MagicMock()
        req.method = 'POST'
        req.relative_uri = '/path/to/resource'
        responder.on_get(req, resp)

        request.assert_called_with(
            req.method,
            'http://127.0.0.1:1234/v2/path/to/resource',
            data=req.stream.read(),
            headers=req.headers,
            stream=True)

        self.assertEquals(resp.status, 200)
        self.assertEquals(resp.content_type, 'application/json')
        self.assertEquals(resp.stream_len, '10')
        resp.set_headers.assert_called_with({})
        self.assertEquals(resp.stream.read(), 'TEST BODY')

    @patch('jumpgate.common.openstack.requests.request')
    def test_standard_responder_with_mount(self, request):
        responder = OpenStackResponder('/mount/point',
                                       'http://127.0.0.1:1234/v2')
        req, resp = MagicMock(), MagicMock()
        req.method = 'POST'
        req.relative_uri = '/mount/point/path/to/resource'
        responder.on_get(req, resp)

        request.assert_called_with(
            req.method,
            'http://127.0.0.1:1234/v2/path/to/resource',
            data=req.stream.read(),
            headers=req.headers,
            stream=True)

    @patch('jumpgate.common.openstack.requests.request')
    def test_standard_responder_plain_text_hack(self, request):
        request.return_value = make_response(content_type='text/html')
        responder = OpenStackResponder(None, 'http://127.0.0.1:1234/v2')
        req, resp = MagicMock(), MagicMock()
        req.method = 'GET'
        req.relative_uri = '/path/to/resource'
        responder.on_get(req, resp)

        request.assert_called_with(
            req.method,
            'http://127.0.0.1:1234/v2/path/to/resource',
            data=None,
            headers=req.headers,
            stream=True)

        self.assertEquals(resp.status, 200)
        self.assertEquals(resp.content_type, 'text/plain; charset=UTF-8')
        self.assertEquals(resp.stream_len, '0')
        resp.set_headers.assert_called_with({})
        self.assertEquals(resp.stream.read(), '')
