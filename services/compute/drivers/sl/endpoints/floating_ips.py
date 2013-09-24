import json


class SLComputeV2OSFloatingIps(object):
    def on_get(self, req, resp, tenant_id):
        resp.body = json.dumps({'floating_ips': []})
