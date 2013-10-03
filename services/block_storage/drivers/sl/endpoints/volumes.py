

class SLBlockStorageV2Volumes(object):
    def on_get(self, req, resp, tenant_id):
        resp.body = {'volumes': []}

    def on_post(self, req, resp, tenant_id):
        resp.body = {'volume': {}}
