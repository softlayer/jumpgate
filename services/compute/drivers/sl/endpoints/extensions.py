import json


class SLComputeV2Extensions(object):
    def on_get(self, req, resp, tenant_id):
        resp.body = json.dumps({'extensions': {}})
