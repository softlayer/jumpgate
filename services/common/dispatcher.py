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

    def get_endpoint(self, nickname):
        if nickname in self.__endpoints:
            return self.__endpoints[nickname]

    def set_handler(self, nickname, handler):
        if nickname not in self.__endpoints:
            # TODO - Need to raise an appropriate exception here
            return None

        data = self.__endpoints[nickname]
        data[1] = handler

        self.__endpoints[nickname] = data
