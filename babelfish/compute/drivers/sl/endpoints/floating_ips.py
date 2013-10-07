

class SLComputeV2OSFloatingIps(object):
    def on_get(self, req, resp, tenant_id):
        resp.body = {'floating_ips': []}
