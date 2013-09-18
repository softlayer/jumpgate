class Dispatcher(object):
    __api = None
    __endpoints = {}

    def __init__(self, api):
        self.__api = api

    def add_endpoint(self, nickname, endpoint, handler=None):
        self.__endpoints[nickname] = [endpoint, handler]

    def import_routes(self):
        for endpoint in self.__endpoints.values():
            if endpoint[1]:
                self.__api.add_route(endpoint[0], endpoint[1])

    def get_endpoint_url(self, nickname, **kwargs):
        url = ''
        if nickname in self.__endpoints:
            url = self.__endpoints[nickname][0]

        # TODO - Add in auto-tenant_id replacement
        for var, value in kwargs.items():
            if '{' + var + '}' in url:
                url = url.replace('{' + var + '}', value)

        return url

    def get_unused_endpoints(self):
        results = []

        for nickname, endpoint in self.__endpoints.items():
            if not endpoint[1]:
                results.append(nickname)

        return results

    def set_handler(self, nickname, handler):
        if nickname not in self.__endpoints:
            # TODO - Need to raise an appropriate exception here
            return None

        data = self.__endpoints[nickname]
        data[1] = handler

        self.__endpoints[nickname] = data
