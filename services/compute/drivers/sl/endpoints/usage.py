import json
import falcon


class SLComputeV2Usage(object):
    def on_get(self, req, resp, tenant_id, target_id):
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'tenant_usage': {}})
