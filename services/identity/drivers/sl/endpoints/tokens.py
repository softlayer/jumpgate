import datetime
import falcon
import logging
from SoftLayer import Client, SoftLayerAPIError

from services.shared.drivers.sl.auth import get_auth
from services.common.error_handling import unauthorized
from services.identity import identity_dispatcher

logger = logging.getLogger(__name__)


class SLIdentityV2Tokens(object):
    def on_post(self, req, resp):
        body = req.stream.read().decode()
        auth, token, err = get_auth(req, resp, body=body)
        if err:
            return err
        client = Client(auth=auth)

        try:
            account = client['Account'].getObject()
            user = client['Account'].getCurrentUser()
        except SoftLayerAPIError as e:
            if e.faultCode == 'SoftLayer_Exception_InvalidLegacyToken':
                return unauthorized(resp,
                                    message='Invalid Credentials',
                                    details=e.faultString)
            raise
        id = account['id']
        index_url = identity_dispatcher.get_endpoint_url(req, 'v2_index')
        service_catalog = [
            {
                'endpoint_links': [],
                'endpoints': [
                    {
                        'region': 'RegionOne',
                        'publicURL': 'http://localhost:5000/v2/%s' % id,
                        'privateURL': 'http://localhost:5000/v2/%s' % id,
                        'adminURL': 'http://localhost:5000/v2/%s' % id,
                        'internalURL': 'http://localhost:5000/v2/%s' % id,
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
                        'publicURL': index_url,
                        'privateURL': index_url,
                        'adminURL': index_url,
                        'internalURL': index_url,
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
                'type': 'network',
                'name': 'network',
            },
        ]

        expiration = datetime.datetime.now() + datetime.timedelta(days=1)
        access = {
            'token': {
                'expires': expiration.isoformat(),
                'id': token,
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
                ],
                'role_links': [],
                'name': user['username']
            },
        }

        resp.status = falcon.HTTP_200
        resp.body = {'access': access}


class SLIdentityV2Token(object):
    def on_delete(self, req, resp, token_id):
        # This method is called when OpenStack wants to remove a token's
        # validity, such as when a cookie expires. Our login tokens don't
        # expire, so this does nothing.
        resp.status = falcon.HTTP_202
        resp.body = ''
