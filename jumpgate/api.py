import importlib
import logging

import falcon

from jumpgate.common import dispatcher
from jumpgate.common import error_handling
from jumpgate.common import exceptions
from jumpgate.common import hooks
from jumpgate.common import nyi
from jumpgate.common import utils
from jumpgate import config

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
        self.config = config.CONF
        self.installed_modules = {}
        self.hooks = hooks.APIHooks()

        # default internal hooks
        self.before_hooks = self.hooks.required_request_hooks()
        self.after_hooks = self.hooks.required_response_hooks()

        self.default_route = None

        self._dispatchers = {}
        self._error_handlers = []

    def add_error_handler(self, ex, handler):
        if (ex, handler) not in self._error_handlers:
            self._error_handlers.insert(0, (ex, handler))

    def make_api(self):
        self.before_hooks.extend(self.hooks.optional_request_hooks())
        self.after_hooks.extend(self.hooks.optional_response_hooks())

        api = falcon.API(before=self.before_hooks, after=self.after_hooks)

        # Set the default route to the NYI object
        api.add_sink(self.default_route or nyi.NYI(before=self.before_hooks,
                                                   after=self.after_hooks))

        # Add Error Handlers - ordered generic to more specific
        built_in_handlers = [(Exception, handle_unexpected_errors),
                             (exceptions.ResponseException,
                              exceptions.ResponseException.handle),
                             (exceptions.InvalidTokenError,
                              exceptions.InvalidTokenError.handle)]

        for ex, handler in built_in_handlers + self._error_handlers:
            wrapped_handler = utils.wrap_handler_with_hooks(handler,
                                                            self.after_hooks)
            api.add_error_handler(ex, wrapped_handler)

        # Add all the routes collected thus far
        for _, disp in self._dispatchers.items():
            for endpoint, handler in disp.get_routes():
                LOG.debug("Loading endpoint %s", endpoint)
                api.add_route(endpoint, handler)
                api.add_route('%s.json' % endpoint, handler)

        return api

    def add_dispatcher(self, service, disp):
        self._dispatchers[service] = disp

    def get_dispatcher(self, service):
        return self._dispatchers[service]

    def get_endpoint_url(self, service, *args, **kwargs):
        disp = self._dispatchers.get(service)
        return disp.get_endpoint_url(*args, **kwargs)

    def load_endpoints(self):
        for service in SUPPORTED_SERVICES:
            enabled_services = self.config['enabled_services']
            if service in enabled_services:
                service_module = importlib.import_module('jumpgate.' + service)

                # Import the dispatcher for the service
                mount = self.config[service]['mount']
                disp = dispatcher.Dispatcher(mount=mount)
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


def handle_unexpected_errors(ex, req, resp, params):
    LOG.exception('Unexpected Error')
    return error_handling.compute_fault(resp,
                                        message='Service Unavailable',
                                        details='Service Unavailable')
