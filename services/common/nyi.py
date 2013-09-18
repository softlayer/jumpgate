import json
import falcon


class NYI(object):
    def on_get(self, req, resp):
        self._standard_responder(req, resp)

    def on_post(self, req, resp):
        self._standard_responder(req, resp)

    def _standard_responder(self, req, resp):
        print("UNKNOWN PATH:", req.path)
        resp.status = falcon.HTTP_501
        resp.body = json.dumps({
            'message': 'Not Implemented',
            'detail': 'Not Implemented',
        })
        