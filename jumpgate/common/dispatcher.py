import collections
import logging
LOG = logging.getLogger(__name__)


class Dispatcher(object):
    def __init__(self, mount=None):
        self._endpoints = collections.OrderedDict()
        self.mount = mount

    def add_endpoint(self, nickname, endpoint):
        if self.mount:
            endpoint = self.mount + endpoint
        self._endpoints[nickname] = (endpoint, None)

    def get_endpoint_path(self, req, nickname, **kwargs):
        path = ''
        if nickname in self._endpoints:
            path = self._endpoints[nickname][0]

        if '{tenant_id}' in path:
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

        for nickname, endpoint in self._endpoints.items():
            if not endpoint[1]:
                results.append(nickname)

        return results

    def set_handler(self, nickname, handler):
        if nickname not in self._endpoints:
            raise ValueError("Unsupported endpoint '%s' specified." % nickname)

        endpoint, _ = self._endpoints[nickname]

        self._endpoints[nickname] = (endpoint, handler)

    def get_routes(self):
        endpoints = []
        for endpoint, h in self._endpoints.values():
            if h:
                endpoints.append((endpoint, h))

        return endpoints
