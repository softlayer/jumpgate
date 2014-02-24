import base64
import datetime
import json
import logging
import time

from jumpgate.common.sl.auth import get_token_details, get_auth
from jumpgate.common.aes import encode_aes
from jumpgate.common.exceptions import Unauthorized
from jumpgate.common.utils import lookup

from SoftLayer import Client, SoftLayerAPIError
from oslo.config import cfg

LOG = logging.getLogger(__name__)
USER_MASK = 'id, username, accountId'


def parse_templates(template_lines):
    o = {}
    for line in template_lines:
        if ' = ' not in line:
            continue

        k, v = line.strip().split(' = ')
        if not k.startswith('catalog.'):
            continue

        parts = k.split('.')

        region, service, key = parts[1:4]

        region_ref = o.get(region, {})
        service_ref = region_ref.get(service, {})
        service_ref[key] = v

        region_ref[service] = service_ref
        o[region] = region_ref

    return o


def get_access(token_id, token_details, user):
    return {
        'token': {
            'expires': datetime.datetime.fromtimestamp(
                token_details['expires']).isoformat(),
            'id': token_id,
            'tenant': {
                'id': token_details['tenant_id'],
                'name': token_details['tenant_id'],
            },
        },
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


class TokensV2(object):
    def __init__(self, template_file):
        self._load_templates(template_file)

    def _load_templates(self, template_file):
        try:
            self.templates = parse_templates(open(template_file))
        except IOError:
            LOG.critical('Unable to open template file %s', template_file)
            raise

    def _get_catalog(self, tenant_id, user_id):
        d = {'tenant_id': tenant_id, 'user_id': user_id}

        o = {}
        for region, region_ref in self.templates.items():
            o[region] = {}
            for service, service_ref in region_ref.items():
                o[region][service] = {}
                for k, v in service_ref.items():
                    o[region][service][k] = v.replace('$(', '%(') % d
        return o

    def _authenticate(self, credentials):
        username = lookup(credentials, 'auth', 'passwordCredentials',
                          'username')
        credential = lookup(credentials, 'auth', 'passwordCredentials',
                            'password')

        def assert_tenant(user):
            tenant = lookup(credentials, 'auth', 'tenantId')
            if tenant and str(user['accountId']) != tenant:
                raise Unauthorized('Invalid username, password or tenant id')

        # If the 'password' is the right length, treat it as an API api_key
        if len(credential) == 64:
            client = Client(username=username, api_key=credential)
            user = client['Account'].getCurrentUser(mask=USER_MASK)
            assert_tenant(user)
            return user, credential, 'api_key'
        else:
            client = Client()
            client.auth = None
            try:
                userId, tokenHash = client.\
                    authenticate_with_password(username, credential)
                user = client['Account'].getCurrentUser(mask=USER_MASK)
                assert_tenant(user)
                return user, tokenHash, 'token'
            except SoftLayerAPIError as e:
                if (e.faultCode == "SoftLayer_Exception_User_Customer"
                        "_LoginFailed"):
                    raise Unauthorized(e.faultString)
                raise

    def _build_auth_token(self, user_id, username, tenant, credential,
                          auth_type):
        return {'user_id': user_id,
                'username': username,
                'api_key': credential,
                'auth_type': auth_type,
                'tenant_id': tenant,
                'expires': time.time() + (60 * 60 * 24)}

    def on_post(self, req, resp):
        body = req.stream.read().decode()
        credentials = json.loads(body)
        user, api_token, auth_type = self._authenticate(credentials)
        token_details = self._build_auth_token(str(user['id']),
                                               str(user['username']),
                                               str(user['accountId']),
                                               api_token,
                                               auth_type)
        token_id = base64.b64encode(encode_aes(json.dumps(token_details)))

        access = get_access(token_id, token_details, user)

        # Add catalog to the access data
        raw_catalog = self._get_catalog(token_details['tenant_id'], user['id'])
        catalog = []
        for services in raw_catalog.values():
            for service_type, service in services.items():
                d = {
                    'type': service_type,
                    'name': service.get('name', 'Unknown'),
                    'endpoints': [{
                        'region': service.get('region', 'RegionOne'),
                        'publicURL': service.get('publicURL'),
                        'privateURL': service.get('privateURL'),
                        'adminURL': service.get('adminURL'),
                    }],
                    'endpoint_links': [],
                }
                catalog.append(d)

        access['serviceCatalog'] = catalog

        resp.status = 200
        resp.body = {'access': access}


class TokenV2(object):
    def on_get(self, req, resp, token_id):
        token_details = get_token_details(token_id,
                                          tenant_id=req.get_param('belongsTo'))
        client = Client(endpoint_url=cfg.CONF['softlayer']['endpoint'])
        client.auth = get_auth(token_details)

        user = client['Account'].getCurrentUser(mask='id, username')
        access = get_access(token_id, token_details, user)

        resp.status = 200
        resp.body = {'access': access}

    def on_delete(self, req, resp, token_id):
        # This method is called when OpenStack wants to remove a token's
        # validity, such as when a cookie expires. Our login tokens can't
        # be forced to expire yet, so this does nothing.
        LOG.warning('User attempted to delete token: %s', token_id)
        resp.status = 202
        resp.body = ''
