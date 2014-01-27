import importlib
import logging

from falcon import API

from jumpgate.config import CONF
from jumpgate.common.utils import wrap_handler_with_hooks
from jumpgate.common.nyi import NYI
from jumpgate.common.hooks import hook_format, hook_set_uuid, hook_log_request
from jumpgate.common.dispatcher import Dispatcher
from jumpgate.common.exceptions import ResponseException
from jumpgate.common.error_handling import compute_fault

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
        self.default_route = None

        self._dispatchers = {}
        self._error_handlers = []

    def add_error_handler(self, ex, handler):
        if (ex, handler) not in self._error_handlers:
            self._error_handlers.insert(0, (ex, handler))

    def make_api(self):
        api = API(before=self.before_hooks, after=self.after_hooks)

        # Set the default route to the NYI object
        api.add_sink(self.default_route or NYI())

        # Add Error Handlers - ordered generic to more specific
        built_in_handlers = [(Exception, handle_unexpected_errors),
                             (ResponseException, ResponseException.handle)]

        for ex, handler in built_in_handlers + self._error_handlers:
            api.add_error_handler(ex,
                                  wrap_handler_with_hooks(handler,
                                                          self.after_hooks))

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


def handle_unexpected_errors(ex, req, resp, params):
    LOG.exception('Unexpected Error')
    return compute_fault(resp,
                         message='Service Unavailable',
                         details='Service Unavailable')
