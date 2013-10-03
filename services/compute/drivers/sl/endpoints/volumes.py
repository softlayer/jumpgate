import falcon


class SLComputeV2OSVolumeAttachments(object):
    def on_get(self, req, resp, tenant_id, instance_id):
        resp.status = falcon.HTTP_200
        resp.body = {'volumeAttachments': []}
