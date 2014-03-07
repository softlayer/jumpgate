import unittest
from mock import MagicMock

from jumpgate.common.nyi import NYI


class TestNYI(unittest.TestCase):
    def setUp(self):
        self.nyi = NYI()

    def test_call(self):
        not_implemented_response = {
            'notImplemented': {
                'message': 'Not Implemented',
                'code': '501',
                'details': 'Not Implemented'
            }
        }

        req, resp = MagicMock(), MagicMock()
        self.nyi(req, resp)

        self.assertEquals(resp.status, 501)
        self.assertEquals(resp.body, not_implemented_response)
