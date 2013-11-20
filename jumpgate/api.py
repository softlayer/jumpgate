import importlib

from falcon import API

from jumpgate.config import CONF
from jumpgate.common.nyi import NYI
from jumpgate.common.hooks import hook_format, hook_set_uuid, hook_log_request


SUPPORTED_SERVICES = [
    'openstack',
    'block_storage',
    'identity',
    'compute',
    'image',
    'network',
    'baremetal',
]


class Jumpgate(object):

    def __init__(self):
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
                api.add_route(endpoint, handler)

        return api

    def add_dispatcher(self, service, dispatcher):
        self._dispatchers[service] = dispatcher

    def get_dispatcher(self, service):
        return self._dispatchers[service]

    def get_endpoint_url(self, service, *args, **kwargs):
        dispatcher = self._dispatchers.get(service)
        return dispatcher.get_endpoint_url(*args, **kwargs)

    def load_drivers(self):
        for service in SUPPORTED_SERVICES:
            if service in CONF:
                self.load_driver(service)
                self.installed_modules[service] = True
            else:
                self.installed_modules[service] = False

    def load_driver(self, service):
        # Import the dispatcher for the service
        dispatcher_module = importlib.import_module('jumpgate.' + service)
        dispatcher = dispatcher_module.get_dispatcher()
        self.add_dispatcher(service, dispatcher)

        # Import the configured driver for the service
        module = importlib.import_module(CONF[service]['driver'])
        if hasattr(module, 'setup_driver'):
            module.setup_driver(self, dispatcher)


def make_api():
    CONF(project='jumpgate', args=[])
    CONF.find_file('jumpgate.cfg')

    app = Jumpgate()
    app.load_drivers()

    api = app.make_api()
    return api
