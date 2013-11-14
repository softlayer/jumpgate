

class OSSecurityGroupsV2(object):
    def on_get(self, req, resp, tenant_id, instance_id=None):
        resp.body = {
            'security_groups': [{
                'description': 'default',
                'id': 1,
                'name': 'default',
                'rules': {},
                'tenant_id': tenant_id,
            }]}
