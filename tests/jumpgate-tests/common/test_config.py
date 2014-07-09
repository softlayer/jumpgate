import unittest

from oslo.config import cfg

from jumpgate.config import CONF


class TestConfig(unittest.TestCase):
    def test_get_config(self):
        self.assertIsInstance(CONF, cfg.ConfigOpts)
