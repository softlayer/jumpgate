from mock import patch, MagicMock
import unittest

from jumpgate.common.hooks import hook_format, hook_set_uuid, hook_log_request


class TestHookFormat(unittest.TestCase):
    def test_format(self):
        req = MagicMock()
        resp = MagicMock()
        resp.body = {"example": "JSON"}
        resp.content_type = None

        hook_format(req, resp)

        resp.body = '{"example": "JSON"}'
        resp.content_type = 'application/json'

    def test_format_int_status(self):
        req = MagicMock()
        resp = MagicMock()
        resp.status = 200

        hook_format(req, resp)

        self.assertEquals(resp.status, '200 OK')

    def test_format_request_id(self):
        req = MagicMock()
        req.env = {'REQUEST_ID': '123456'}
        resp = MagicMock()

        hook_format(req, resp)

        resp.set_header.assert_called_with('X-Compute-Request-Id', '123456')


class TestHookLogRequest(unittest.TestCase):
    @patch('jumpgate.common.hooks.LOG')
    def test_log_request(self, log):
        req = MagicMock()
        req.method = 'GET'
        req.path = '/'
        req.query_string = 'something=value'
        req.env = {'REQUEST_ID': '123456'}
        resp = MagicMock()
        resp.status = '200 OK'
        hook_log_request(req, resp)

        log.info.assert_called_with(
            '%s %s %s %s [ReqId: %s]',
            'GET', '/', 'something=value', '200 OK', '123456')


class TestHookSetUUID(unittest.TestCase):
    def test_set_uuid(self):
        req = MagicMock()
        resp = MagicMock()
        req.env = {}

        hook_set_uuid(req, resp, {})

        self.assertEquals(len(req.env), 1)
        self.assertEquals(req.env.keys(), ['REQUEST_ID'])
        self.assertIsNotNone(req.env['REQUEST_ID'])
