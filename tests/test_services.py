import unittest
import importlib

from jumpgate.common.dispatcher import Dispatcher
from jumpgate.api import SUPPORTED_SERVICES


class TestServiceDispatchers(unittest.TestCase):
    def test_all_dispatchers(self):
        for service in SUPPORTED_SERVICES:
            disp = Dispatcher()
            dispatcher_module = importlib.import_module('jumpgate.' + service)
            dispatcher_module.add_endpoints(disp)

            self.assertGreater(len(disp._endpoints), 0)
