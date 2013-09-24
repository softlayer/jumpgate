import json


class SLBlockStorageV2Volumes(object):
    def on_get(self, req, resp, tenant_id):
        resp.body = json.dumps({'volumes': []})
