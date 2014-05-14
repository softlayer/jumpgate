from oslo.config import cfg


class OSQuotaSetsV2(object):
    def on_get(self, req, resp, tenant_id, account_id=None):
        qs = {
            "cores": cfg.CONF['compute']['default_cores'],
            "floating_ips": cfg.CONF['compute']['default_floating_ips'],
            "id": tenant_id,
            "injected_file_content_bytes":
            cfg.CONF['compute']['default_injected_file_content_bytes'],
            "injected_file_path_bytes":
            cfg.CONF['compute']['default_injected_file_path_bytes'],
            "injected_files": cfg.CONF['compute']['default_injected_files'],
            "instances": cfg.CONF['compute']['default_instances'],
            "key_pairs": cfg.CONF['compute']['default_key_pairs'],
            "metadata_items": cfg.CONF['compute']['default_metadata_items'],
            "ram": cfg.CONF['compute']['default_ram'],
            "security_group_rules":
            cfg.CONF['compute']['default_security_group_rules'],
            "security_groups": cfg.CONF['compute']['default_security_groups']
        }

        resp.body = {'quota_set': qs}
