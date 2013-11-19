import requests

from core import api


def setup_responder(app, disp):
    responder = OpenStackResponder()

    for endpoint in disp.get_unused_endpoints():
        disp.set_handler(endpoint, responder)


class OpenStackResponder(object):
    def __init__(self, app):
        config = api.config['driver_config']
        self.endpoint = config['openstack'].get('default_endpoint')

    def on_delete(self, req, resp, **kwargs):
        self._standard_responder(req, resp)

    def on_get(self, req, resp, **kwargs):
        self._standard_responder(req, resp)

    def on_head(self, req, resp, **kwargs):
        self._standard_responder(req, resp)

    def on_post(self, req, resp, **kwargs):
        self._standard_responder(req, resp)

    def on_put(self, req, resp, **kwargs):
        self._standard_responder(req, resp)

    def _standard_responder(self, req, resp):
        payload = {
            'headers': req.headers,
        }

        if req.method == 'POST' or req.method == 'PUT':
            payload['data'] = req.stream.read().decode()

        (host, port) = req.get_header('host').split(':')
        url = 'http://' + req.env['HTTP_HOST'].replace(host, self.endpoint) + \
              req.path

        if req.method == 'GET' and req.query_string:
            url += '?' + req.query_string

        result_code = 200
        body = ''

        try:
            f = getattr(requests, req.method.lower())
            r = f(url, **payload)
            # Crude IP replacement
            body = r.text.replace(self.endpoint, host)
            #body = r.text
            result_code = r.status_code
        except requests.exceptions.HTTPError as error:
            result_code = error.code

        resp.set_headers(r.headers)
        resp.status = str(result_code)
        resp.body = body
