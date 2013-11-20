import unittest
import importlib

from jumpgate.common.dispatcher import Dispatcher
from jumpgate.api import SUPPORTED_SERVICES


class TestServiceDispatchers(unittest.TestCase):
    def test_all_dispatchers(self):
        for service in SUPPORTED_SERVICES:
            dispatcher_module = importlib.import_module('jumpgate.' + service)
            dispatcher = dispatcher_module.get_dispatcher()

            self.assertIsInstance(dispatcher, Dispatcher)
            self.assertGreater(len(dispatcher.get_routes()), 0)
