import json
import falcon

from services.compute import compute_dispatcher as disp


class SLComputeV2OSVolumeAttachments(object):
    def on_get(self, req, resp, tenant_id, instance_id):
        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'volumeAttachments': []})
