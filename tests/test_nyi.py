import unittest
from mock import MagicMock

from jumpgate.common.nyi import NYI


class TestNYI(unittest.TestCase):
    def setUp(self):
        self.nyi = NYI()

    def test_all_verbs(self):
        methods = [
            self.nyi.on_get,
            self.nyi.on_post,
            self.nyi.on_put,
            self.nyi.on_delete,
            self.nyi.on_head,
        ]
        not_implemented_response = {
            'notImplemented': {
                'message': 'Not Implemented',
                'code': '501',
                'details': 'Not Implemented'
            }
        }

        for method in methods:
            req, resp = MagicMock(), MagicMock()
            method(req, resp)

            self.assertEquals(resp.status, 501)
            self.assertEquals(resp.body, not_implemented_response)
