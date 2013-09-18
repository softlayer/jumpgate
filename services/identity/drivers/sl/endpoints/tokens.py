import datetime
import json
import falcon
from SoftLayer import Client, SoftLayerAPIError, TokenAuthentication

from services.common.nested_dict import lookup
from services.identity import identity_dispatcher


class SLIdentityV2Tokens(object):
    def on_delete(self, req, resp, token_id):
        # This method is called when OpenStack wants to remove a token's
        # validity, such as when a cookie expires. Our login tokens don't
        # expire, so this does nothing.
        resp.status = falcon.HTTP_202
        resp.body = ''

    def on_post(self, req, resp, token_id=None):
        headers = req.headers

        if 'x-auth-token' in headers:
            (userId, hash) = headers['x-auth-token'].split(':')            
        else:
            body = json.loads(req.stream.read().decode())

            username = lookup(body, 'auth', 'passwordCredentials', 'username')
            password = lookup(body, 'auth', 'passwordCredentials', 'password')

            try:
                client = Client()
                (userId, hash) = client.authenticate_with_password(username,
                                                                   password)
            except SoftLayerAPIError as e:
                # TODO - Do the right thing here
                # if e.faultCode == \
                #         'SoftLayer_Exception_User_Customer_LoginFailed':
                #     return unauthorized(message=e.faultCode,
                #                         details=e.faultString)

                # return compute_fault(message=e.faultCode,
                #                      details=e.faultString)
                return None

        auth = TokenAuthentication(userId, hash)
        if auth:
            client = Client(auth=auth)

        account = client['Account'].getObject()
        user = client['Account'].getCurrentUser()
        id = str(account['id'])

        # TODO - This dictionary shouldn't be hardcoded
        v3_index = identity_dispatcher.get_endpoint_url('v3_index')
        service_catalog = [
            {
                'endpoint_links': [],
                'endpoints': [
                    {
                        'region': 'RegionOne',
                        'publicURL': 'http://localhost:5000/v2/' + id,
                        'privateURL': 'http://localhost:5000/v2/' + id,
                        'adminURL': 'http://localhost:5000/v2/' + id,
                        'internalURL': 'http://localhost:5000/v2/' + id,
                        'id': 1,
                    },
                ],
                'type': 'compute',
                'name': 'compute',
            },
            {
                'endpoint_links': [],
                'endpoints': [
                    {
                        'region': 'RegionOne',
                        'publicURL': v3_index,
                        'privateURL': v3_index,
                        'adminURL': v3_index,
                        'internalURL': v3_index,
                        'id': 1,
                    },
                ],
                'type': 'identity',
                'name': 'identity',
            },
            {
                'endpoint_links': [],
                'endpoints': [
                    {
                        'region': 'RegionOne',
                        'publicURL': 'http://localhost:5000',
                        'privateURL': 'http://localhost:5000',
                        'adminURL': 'http://localhost:5000',
                        'internalURL': 'http://localhost:5000',
                        'id': 1,
                    },
                ],
                'type': 'image',
                'name': 'image',
            },
            # This would expose a "volumes" endpoint.
            # {
            #     'endpoint_links': [],
            #     'endpoints': [
            #         {
            #             'region': 'RegionOne',
            #             'publicURL': 'http://localhost:5000/v1/' + id,
            #             'privateURL': 'http://localhost:5000/v1/' + id,
            #             'adminURL': 'http://localhost:5000/v1/' + id,
            #             'internalURL': 'http://localhost:5000/v1/' + id,
            #             'id': 1,
            #         },
            #     ],
            #     'type': 'volume',
            #     'name': 'volume',
            # }
        ]

        expiration = datetime.datetime.now() + datetime.timedelta(days=1)
        access = {
            'token': {
                'expires': expiration.isoformat(),
                'id': str(userId) + ':' + hash,
                'tenant': {
                    'id': id,
                    'enabled': True,
                    'description': account['companyName'],
                    'name': account['id'],
                },
            },
            'serviceCatalog': service_catalog,
            'user': {
                'username': user['username'],
                'id': id,
                'roles': [
                    {'name': 'user'},
#                    {'name': 'admin'}
                ],
                'role_links': [],
                'name': user['username']
            },
        }

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'access': access})
        