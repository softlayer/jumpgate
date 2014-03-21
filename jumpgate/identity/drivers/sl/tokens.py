import datetime
import json
import logging

from jumpgate.common.exceptions import Unauthorized
from jumpgate.common.utils import lookup
from jumpgate.identity.drivers import core as identity

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


def get_access(token_id, token_details):
    tokens = identity.token_driver()
    return {
        'token': {
            'expires': datetime.datetime.fromtimestamp(
                tokens.expires(token_details)).isoformat(),
            'id': token_id,
            'tenant': {
                'id': tokens.tenant_id(token_details),
                'name': tokens.tenant_name(token_details),
            },
        },
        'user': {
            'username': tokens.username(token_details),
            'id': tokens.user_id(token_details),
            'roles': [{'id': rid, 'name': name} for rid, name in
                      tokens.roles(token_details).items()],
            'role_links': [],
            'name': tokens.username(token_details),
        },
    }


class SLAuthDriver(identity.AuthDriver):
    """Jumpgate SoftLayer auth driver which authenticates using the SLAPI.
    Suitable for most implementations who's authentication requests should
    be validates against SoftLayer's credential system which uses either a
    username/password scheme or a username/api-key scheme.
    """

    def __init__(self):
        super(SLAuthDriver, self).__init__()

    def authenticate(self, creds):
        username = lookup(creds, 'auth', 'passwordCredentials',
                          'username')
        credential = lookup(creds, 'auth', 'passwordCredentials',
                            'password')
        token_id = lookup(creds, 'auth', 'token', 'id')
        if token_id:
            token = identity.token_id_driver().token_from_id(token_id)
            token_driver = identity.token_driver()
            token_driver.validate_token(token)
            username = token_driver.username(token)
            credential = token_driver.credential(token)

        def assert_tenant(user):
            tenant = lookup(creds, 'auth', 'tenantId') or lookup(creds,
                                                                 'auth',
                                                                 'tenantName')
            if tenant and str(user['accountId']) != tenant:
                raise Unauthorized('Invalid username, password or tenant id')

        # If the 'password' is the right length, treat it as an API api_key
        if len(credential) == 64:
            client = Client(username=username, api_key=credential,
                            endpoint_url=cfg.CONF['softlayer']['endpoint'],
                            proxy=cfg.CONF['softlayer']['proxy'])
            user = client['Account'].getCurrentUser(mask=USER_MASK)
            assert_tenant(user)
            return {'user': user, 'credential': credential,
                    'auth_type': 'api_key'}
        else:
            client = Client(endpoint_url=cfg.CONF['softlayer']['endpoint'],
                            proxy=cfg.CONF['softlayer']['proxy'])
            client.auth = None
            try:
                userId, tokenHash = client.\
                    authenticate_with_password(username, credential)
                user = client['Account'].getCurrentUser(mask=USER_MASK)
                assert_tenant(user)
                return {'user': user, 'credential': tokenHash,
                        'auth_type': 'token'}
            except SoftLayerAPIError as e:
                if (e.faultCode == "SoftLayer_Exception_User_Customer"
                        "_LoginFailed"):
                    raise Unauthorized(e.faultString)
                raise


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

    def on_post(self, req, resp):
        body = req.stream.read().decode()
        credentials = json.loads(body)
        tokens = identity.token_driver()

        auth = identity.auth_driver().authenticate(credentials)
        if auth is None:
            raise Unauthorized('Unauthorized credentials')
        token = tokens.create_token(credentials, auth)
        tok_id = identity.token_id_driver().create_token_id(token)
        access = get_access(tok_id, token)

        # Add catalog to the access data
        raw_catalog = self._get_catalog(tokens.tenant_id(token),
                                        tokens.user_id(token))
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
        token = identity.token_id_driver().token_from_id(token_id)
        identity.token_driver().validate_access(token, tenant_id=
                                                req.get_param('belongsTo'))
        access = get_access(token_id, token)

        resp.status = 200
        resp.body = {'access': access}

    def on_delete(self, req, resp, token_id):
        # This method is called when OpenStack wants to remove a token's
        # validity, such as when a cookie expires. Our login tokens can't
        # be forced to expire yet, so this does nothing.
        LOG.warning('User attempted to delete token: %s', token_id)
        resp.status = 202
        resp.body = ''
