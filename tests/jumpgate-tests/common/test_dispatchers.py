import unittest
import importlib
import os.path
from mock import MagicMock

from jumpgate.common.dispatcher import Dispatcher
from jumpgate.api import Jumpgate, SUPPORTED_SERVICES

DIR_PATH = os.path.dirname(__file__)
MOCK_CONFIG = MagicMock()
MOCK_CONFIG.softlayer.catalog_template_file = os.path.join(
    DIR_PATH, '../identity.templates')
MOCK_CONFIG.softlayer.catalog_template_file_v3 = os.path.join(
    DIR_PATH, '../identity_v3.templates')
MOCK_CONFIG.flavors.flavor_list = os.path.join(DIR_PATH,
                                               '../flavor_list.json')
MOCK_CONFIG.volume.volume_types = os.path.join(
    DIR_PATH, '../volume_types.json')


class TestServiceDispatchers(unittest.TestCase):
    def test_all_endpoints(self):
        for service in SUPPORTED_SERVICES:
            app = Jumpgate()
            app.config = MOCK_CONFIG
            disp = Dispatcher()
            dispatcher_module = importlib.import_module('jumpgate.' + service)
            dispatcher_module.add_endpoints(disp)

            module_name = 'jumpgate.%s.drivers.sl' % service
            module = importlib.import_module(module_name)
            module.setup_routes(app, disp)

            self.assertGreater(len(disp._endpoints), 0)
