import json
import falcon
from core import api
# TODO - I need to centralize this better
#from . import get_client


class SLIdentityV2Tenants(object):
    def on_get(self, req, resp):
        client = api.config['sl_client']
        account = client['Account'].getObject()

        tenants = [
            {
                'enabled': True,
                'description': None,
                'name': account['id'],
                'id': account['id'],
            },
        ]

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'tenants': tenants, 'tenant_links': []})
