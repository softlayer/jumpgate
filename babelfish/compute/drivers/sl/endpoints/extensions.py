

class SLComputeV2Extensions(object):
    def on_get(self, req, resp, tenant_id):
        resp.body = {'extensions': {}}
