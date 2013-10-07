

class SLComputeV2ExtraSpecsFlavor(object):
    def on_get(self, req, resp, tenant_id, flavor_id):
        resp.body = {'extra_specs': ''}
