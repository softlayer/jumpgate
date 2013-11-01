import datetime
import logging
from SoftLayer import Client

from babelfish.shared.drivers.sl.errors import convert_errors
from babelfish.shared.drivers.sl.auth import get_auth
from babelfish.identity import identity_dispatcher
from babelfish.openstack import openstack_dispatcher

logger = logging.getLogger(__name__)


class TokensV2(object):
    @convert_errors
    def on_post(self, req, resp):
        body = req.stream.read().decode()
        auth, token, err = get_auth(req, resp, body=body)
        if err:
            return err
        client = Client(auth=auth)

        user = client['Account'].getCurrentUser(mask='id, account, username')
        account = user['account']

        index_url = identity_dispatcher.get_endpoint_url(req, 'v2_auth_index')
        v2_url = openstack_dispatcher.get_endpoint_url(req, 'v2_index')

        service_catalog = [{
            'endpoint_links': [],
            'endpoints': [{
                'region': 'RegionOne',
                'publicURL': v2_url + '/%s' % account['id'],
                'privateURL': v2_url + '/v2/%s' % account['id'],
                'adminURL': v2_url + '/v2/%s' % account['id'],
                'internalURL': v2_url + '/v2/%s' % account['id'],
                'id': 1,
            }],
            'type': 'compute',
            'name': 'nova',
        }, {
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
            'name': 'keystone',
        }, {
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
            'name': 'glance',
        }, #{
        #     'endpoint_links': [],
        #     'endpoints': [
        #         {
        #             'region': 'RegionOne',
        #             'publicURL': 'http://localhost:5000',
        #             'privateURL': 'http://localhost:5000',
        #             'adminURL': 'http://localhost:5000',
        #             'internalURL': 'http://localhost:5000',
        #             'id': 1,
        #         },
        #     ],
        #     'type': 'network',
        #     'name': 'neutron',
        # }
        ]

        expiration = datetime.datetime.now() + datetime.timedelta(days=1)
        access = {
            'token': {
                'expires': expiration.isoformat(),
                'id': token,
                'tenant': {
                    'id': account['id'],
                    'enabled': True,
                    'description': account['companyName'],
                    'name': account['id'],
                },
            },
            'serviceCatalog': service_catalog,
            'user': {
                'username': user['username'],
                'id': user['id'],
                'roles': [
                    {'name': 'user'},
                ],
                'role_links': [],
                'name': user['username'],
            },
        }

        resp.body = {'access': access}


class TokenV2(object):
    def on_delete(self, req, resp, token_id):
        # This method is called when OpenStack wants to remove a token's
        # validity, such as when a cookie expires. Our login tokens don't
        # expire, so this does nothing.
        resp.status = 202
        resp.body = ''
