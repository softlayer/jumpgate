from six.moves import configparser
import importlib

from falcon import API

from jumpgate.common.nyi import NYI
from jumpgate.common.hooks import hook_format, hook_set_uuid, hook_log_request


SUPPORTED_SERVICES = [
    'openstack',
    'block_storage',
    'identity',
    'compute',
    'image',
    'network',
    'baremetal'
]


class Jumpgate(object):

    def __init__(self, config):
        self.config = config
        self.installed_modules = {}

        self.before_hooks = [hook_set_uuid]
        self.after_hooks = [hook_format, hook_log_request]

        self._dispatchers = {}

    def make_api(self):
        api = API(before=self.before_hooks, after=self.after_hooks)

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


def make_api():
    # If there is a jumpgate config file, we should read that too.
    driver_config = configparser.ConfigParser()
    driver_config.read('driver.conf')

    # Load the driver config file to determine which modules are available
    conf = configparser.ConfigParser()
    conf.read('jumpgate.conf')

    # The core application of the translation layer
    app = Jumpgate(conf)

    for service in SUPPORTED_SERVICES:
        if service in conf:
            # Import the dispatcher for the service
            dispatcher_module = importlib.import_module('jumpgate.' + service)
            dispatcher = dispatcher_module.get_dispatcher()
            app.add_dispatcher(service, dispatcher)

            # Import the configured driver for the service
            module = importlib.import_module(conf[service]['driver'])
            if hasattr(module, 'setup_driver'):
                module.setup_driver(app, dispatcher)

            app.installed_modules[service] = True
        else:
            app.installed_modules[service] = False

    api = app.make_api()

    # An easy class that can be used to implement endpoints that are
    # not yet implemented.
    nyi = NYI()

    # Set the default route to the NYI object
    api.set_default_route(nyi)
    return api
