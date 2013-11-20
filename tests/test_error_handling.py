import unittest
from mock import MagicMock

from jumpgate.common import error_handling

ERRORS = [
    (error_handling.not_implemented, 'notImplemented', 501),
    (error_handling.compute_fault, 'computeFault', 500),
    (error_handling.bad_request, 'badRequest', 400),
    (error_handling.unauthorized, 'unauthorized', 401),
    (error_handling.not_found, 'notFound', 404),
    (error_handling.duplicate, 'duplicate', 409),
]


class TestErorrHandlers(unittest.TestCase):
    def setUp(self):
        self.resp = MagicMock()

    def test_without_custom_message(self):
        for error, msg, code in ERRORS:
            error(self.resp, 'CUSTOM MESSAGE',)
            self.assertEquals(self.resp.status, code)
            self.assertEquals(self.resp.body, {
                msg: {
                    'message': 'CUSTOM MESSAGE',
                    'code': str(code),
                }
            })

    def test_with_custom_message(self):
        for error, msg, code in ERRORS:
            error(self.resp,
                  'CUSTOM MESSAGE',
                  details='CUSTOM DETAILED MESSAGE')
            self.assertEquals(self.resp.status, code)
            self.assertEquals(self.resp.body, {
                msg: {
                    'message': 'CUSTOM MESSAGE',
                    'details': 'CUSTOM DETAILED MESSAGE',
                    'code': str(code),
                }
            })
