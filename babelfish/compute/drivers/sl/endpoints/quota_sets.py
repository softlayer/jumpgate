

class OSQuotaSetsV2(object):
    def on_get(self, req, resp, tenant_id, account_id=None):
        # TODO - This is hardcoded and needs changed
        qs = {
            "cores": 200,
            "floating_ips": 100,
            "id": tenant_id,
            "injected_file_content_bytes": 10240,
            "injected_file_path_bytes": 255,
            "injected_files": 5,
            "instances": 10,
            "key_pairs": 100,
            "metadata_items": 128,
            "ram": 512000,
            "security_group_rules": 20,
            "security_groups": 10
        }

        resp.body = {'quota_set': qs}
