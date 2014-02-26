
from jumpgate.common.error_handling import error

class UserProjectsV3(object):
    def on_get(self, req, resp, user_id):
        client = req.env['sl_client']
        account = client['Account'].getObject()
        currentUser = client['Account'].getCurrentUser()
        if currentUser['username']!=user_id:
            return error(resp, 'notMatch', 'User provided does not match current user', details=None, code=500)

        projects = [
            {
                'domain_id':str(account['id']),
                'enabled': True,
                'description': None,
                'name': currentUser['username'],
                'id': str(account['id']),
            },
        ]

        resp.body = {'projects': projects, 'tenant_links': []}
