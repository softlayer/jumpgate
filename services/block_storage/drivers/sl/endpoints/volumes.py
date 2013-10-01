import json


class SLBlockStorageV2Volumes(object):
    def on_get(self, req, resp, tenant_id):
        client = req.env['sl_client']
        sl_volumes = client['Account'].getPortableStorageVolumes()
        print(sl_volumes)
        resp.body = json.dumps({'volumes': []})

    def on_post(self, req, resp, tenant_id):
        body = json.loads(req.stream.read().decode())
        print(body)
        resp.body = json.dumps({'volume': {}})
