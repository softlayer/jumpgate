from collections import OrderedDict
import logging
logger = logging.getLogger(__name__)


class Dispatcher(object):
    def __init__(self, api):
        self.__api = api
        self.__endpoints = OrderedDict()

    def add_endpoint(self, nickname, endpoint, handler=None):
        self.__endpoints[nickname] = (endpoint, handler)

    def get_api(self):
        return self.__api

    def import_routes(self):
        for endpoint in self.__endpoints.values():
            if endpoint[1]:
                logger.info("Importing", endpoint[0])
                self.__api.add_route(endpoint[0], endpoint[1])

    def get_endpoint_path(self, req, nickname, **kwargs):
        path = ''
        if nickname in self.__endpoints:
            path = self.__endpoints[nickname][0]

        if '{tenant_id}' in path:
            if req.env.get('tenant_id'):
                tenant_id = req.env['tenant_id']
                path = path.replace('{tenant_id}', tenant_id)

        for var, value in kwargs.items():
            if '{%s}' % var in path:
                path = path.replace('{%s}' % var, str(value))
        return path

    def get_endpoint_url(self, req, nickname, **kwargs):
        return (req.protocol + '://' +
                req.get_header('host') +
                req.app +
                self.get_endpoint_path(req, nickname, **kwargs))

    def get_unused_endpoints(self):
        results = []

        for nickname, endpoint in self.__endpoints.items():
            if not endpoint[1]:
                results.append(nickname)

        return results

    def set_handler(self, nickname, handler):
        if nickname not in self.__endpoints:
            raise ValueError("Unsupported endpoint '%s' specified." % nickname)

        data = self.__endpoints[nickname]

        self.__endpoints[nickname] = (data[0], handler)
