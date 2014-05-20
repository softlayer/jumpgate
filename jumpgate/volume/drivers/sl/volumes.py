from SoftLayer import ISCSIManager


class VolumesV2(object):
    def on_get(self, req, resp, tenant_id):
        client = req.env['sl_client']
        iscsi_mgr = ISCSIManager(client)
        iscsi_list = iscsi_mgr.list_iscsi()
        if not isinstance(iscsi_list, list):
            iscsi_list = [iscsi_list]
        results = []
        for instance in iscsi_list:
            results.append({
                'id': instance['id'],
                'display_name': instance['serviceResourceName'],
                'size': instance['capacityGb'],
                'volume_type': instance['nasType'],
                'attachments': [],
                "created_at": instance['createDate']
            })
        resp.status = 200
        resp.body = {'volumes': results}

    def on_post(self, req, resp, tenant_id):
        resp.body = {'volume': {}}
