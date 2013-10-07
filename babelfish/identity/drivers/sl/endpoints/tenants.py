import falcon


class SLIdentityV2Tenants(object):
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

        resp.status = falcon.HTTP_200
        resp.body = {'tenants': tenants, 'tenant_links': []}
