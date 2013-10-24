

class TenantsV2(object):
    def on_get(self, req, resp):
        client = req.env['sl_client']
        account = client['Account'].getObject()

        tenants = [
            {
                'enabled': True,
                'description': None,
                'name': str(account['id']),
                'id': str(account['id']),
            },
        ]

        resp.body = {'tenants': tenants, 'tenant_links': []}
