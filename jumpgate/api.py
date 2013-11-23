import importlib
import logging

from falcon import API

from jumpgate.config import CONF
from jumpgate.common.nyi import NYI
from jumpgate.common.hooks import hook_format, hook_set_uuid, hook_log_request
from jumpgate.common.dispatcher import Dispatcher

LOG = logging.getLogger(__name__)

SUPPORTED_SERVICES = [
    'baremetal',
    'compute',
    'identity',
    'image',
    'network',
    'volume',
]


class Jumpgate(object):

    def __init__(self):
        self.config = CONF
        self.installed_modules = {}

        self.before_hooks = [hook_set_uuid]
        self.after_hooks = [hook_format, hook_log_request]

        self._dispatchers = {}

    def make_api(self):
        api = API(before=self.before_hooks, after=self.after_hooks)

        # An easy class that can be used to implement endpoints that are
        # not yet implemented.
        nyi = NYI()

        # Set the default route to the NYI object
        api.set_default_route(nyi)

        # Add all the routes collected thus far
        for _, disp in self._dispatchers.items():
            for endpoint, handler in disp.get_routes():
                LOG.debug("Loading endpoint %s", endpoint)
                api.add_route(endpoint, handler)

        return api

    def add_dispatcher(self, service, dispatcher):
        self._dispatchers[service] = dispatcher

    def get_dispatcher(self, service):
        return self._dispatchers[service]

    def get_endpoint_url(self, service, *args, **kwargs):
        dispatcher = self._dispatchers.get(service)
        return dispatcher.get_endpoint_url(*args, **kwargs)

    def load_endpoints(self):
        for service in SUPPORTED_SERVICES:
            enabled_services = self.config['enabled_services']
            if service in enabled_services:
                service_module = importlib.import_module('jumpgate.' + service)

                # Import the dispatcher for the service
                disp = Dispatcher(mount=self.config[service]['mount'])
                service_module.add_endpoints(disp)
                self.add_dispatcher(service, disp)
                self.installed_modules[service] = True
            else:
                self.installed_modules[service] = False

    def load_drivers(self):
        for service, disp in self._dispatchers.items():
            module = importlib.import_module(self.config[service]['driver'])

            if hasattr(module, 'setup_routes'):
                module.setup_routes(self, disp)
