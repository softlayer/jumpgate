import json
import falcon


class NYI(object):
    def on_get(self, req, resp):
        self._standard_responder(req, resp)

    def on_post(self, req, resp):
        self._standard_responder(req, resp)

    def on_put(self, req, resp):
        self._standard_responder(req, resp)

    def on_delete(self, req, resp):
        self._standard_responder(req, resp)

    def on_head(self, req, resp):
        self._standard_responder(req, resp)

    def _standard_responder(self, req, resp):
        print("UNKNOWN PATH:", req.method, req.path)
        resp.status = falcon.HTTP_501
        resp.body = json.dumps({'notImplemented': {
            'message': 'Not Implemented',
            'detail': 'Not Implemented',
        }})
