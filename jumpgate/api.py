import configparser
import importlib
import logging
import uuid

from falcon import API

from jumpgate.common.nyi import NYI
from jumpgate.common.format import format_hook

LOG = logging.getLogger(__name__)
SUPPORTED_SERVICES = [
    'openstack',
    'block_storage',
    'shared',
    'identity',
    'compute',
    'image',
    'network',
    'baremetal'
]


def hook_set_uuid(req, resp, kwargs):
    req.env['REQUEST_ID'] = str(uuid.uuid1())


def hook_log_request(req, resp):
    LOG.info('%s %s %s %s [ReqId: %s]',
             req.method,
             req.path,
             req.query_string,
             resp.status,
             req.env['REQUEST_ID'])


class Jumpgate(object):

    def __init__(self, config):
        self.config = config
        self.installed_modules = {}

        self.before_hooks = [hook_set_uuid]
        self.after_hooks = [format_hook, hook_log_request]

        self._routes = []
        self._dispatchers = {}

    def make_api(self):
        api = API(before=self.before_hooks, after=self.after_hooks)
        # An easy class that can be used to implement endpoints that are
        # not yet implemented.
        nyi = NYI()

        # Set the default route to the NYI object
        api.set_default_route(nyi)

        # Add all the routes collected thus far
        for uri_template, resource in self._routes:
            api.add_route(uri_template, resource)

        return api

    def add_route(self, uri_template, resource):
        self._routes.append((uri_template, resource))

    def add_dispatcher(self, service, dispatcher):
        self._dispatchers[service] = dispatcher

    def get_dispatcher(self, service):
        return self._dispatcher[service]

    def get_endpoint_url(self, service, *args, **kwargs):
        dispatcher = self._dispatchers.get(service)
        return dispatcher.get_endpoint_url(*args, **kwargs)


def make_api():
    # If there is a jumpgate config file, we should read that too.
    conf = configparser.ConfigParser()
    conf.read('jumpgate.conf')

    # The core application of the translation layer
    app = Jumpgate(conf)

    # Load the driver config file to determine which modules are available
    driver_config = configparser.ConfigParser()
    driver_config.read('driver.conf')

    for service in SUPPORTED_SERVICES:
        if service in driver_config:
            # Import the dispatcher for the service
            dispatcher_module = importlib.import_module('jumpgate.' + service)
            if hasattr(dispatcher_module, 'get_dispatcher'):
                dispatcher = dispatcher_module.get_dispatcher(app)
                app.add_dispatcher(service, dispatcher)

            # Import the configured driver for the service
            module = importlib.import_module(driver_config[service]['driver'])
            if hasattr(module, 'setup'):
                module.setup(app, dispatcher)

            app.installed_modules[service] = True
        else:
            app.installed_modules[service] = False

    return app.make_api()


api = make_api()
