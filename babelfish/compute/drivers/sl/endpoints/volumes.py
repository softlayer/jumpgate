

class OSVolumeAttachmentsV2(object):
    def on_get(self, req, resp, tenant_id, instance_id):
        resp.body = {'volumeAttachments': []}
