from mock import patch
import os.path
import unittest

import falcon

from jumpgate.wsgi import make_api

DIR_PATH = os.path.dirname(__file__)
TEST_CFG_LOC = os.path.join(DIR_PATH, 'test.jumpgate.conf')


class TestWSGI(unittest.TestCase):
    @patch('os.environ', {'JUMPGATE_CONFIG': TEST_CFG_LOC})
    def test_make_api(self):
        new_api = make_api()

        self.assertTrue(hasattr(new_api, '__call__'))
        self.assertIsInstance(new_api, falcon.API)
