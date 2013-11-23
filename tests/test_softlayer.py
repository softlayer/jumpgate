import unittest
import importlib

from jumpgate.common.dispatcher import Dispatcher
from jumpgate.api import Jumpgate, SUPPORTED_SERVICES


class TestSoftLayerBootstrap(unittest.TestCase):
    def test_all_setup_routes(self):
        for service in SUPPORTED_SERVICES:
            app = Jumpgate()
            disp = Dispatcher()
            dispatcher_module = importlib.import_module('jumpgate.' + service)
            dispatcher_module.add_endpoints(disp)

            module_name = 'jumpgate.%s.drivers.sl' % service
            module = importlib.import_module(module_name)
            module.setup_routes(app, disp)

            self.assertGreater(len(disp._endpoints), 0)
