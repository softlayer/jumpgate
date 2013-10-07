import requests

import falcon


class OSMapper(object):
    endpoint = '184.173.116.14'

    def on_delete(self, req, resp):
        self._standard_responder(req, resp)

    def on_get(self, req, resp):
        self._standard_responder(req, resp)

    def on_head(self, req, resp):
        self._standard_responder(req, resp)

    def on_post(self, req, resp):
        self._standard_responder(req, resp)

    def on_put(self, req, resp):
        self._standard_responder(req, resp)

    def _log_request(self, req):
        print(req.method, ":", req.path)
        fp = open('/tmp/openstack_paths.txt', 'a')
        fp.write(req.path + "\n")
        fp.close()

    def _standard_responder(self, req, resp):
        self._log_request(req)

        payload = {
            'headers': req.headers,
        }

        if 'POST' == req.method or 'PUT' == req.method:
            payload['data'] = req.stream.read().decode()

        url = 'http://' + req.env['HTTP_HOST'].replace('127.0.0.1',
                                                       self.endpoint) + \
            req.path

        result_code = falcon.HTTP_200
        body = ''

        try:
            f = getattr(requests, req.method.lower())
            r = f(url, **payload)
            # Crude IP replacement
            body = r.text.replace('http://184.173.116.14', 'http://127.0.0.1')
            result_code = r.status_code
        except requests.exceptions.HTTPError as error:
            result_code = error.code

        resp.set_headers(r.headers)
        resp.status = str(result_code)
        resp.body = body
        