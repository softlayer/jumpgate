import base64
import datetime
import json
import logging

from jumpgate.common import aes
from jumpgate.common import exceptions
from jumpgate.common import utils
from jumpgate.identity.drivers import core as identity

from oslo.config import cfg
import SoftLayer


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
        service_ref['region'] = region

        region_ref[service] = service_ref
        o[region] = region_ref

    return o


def get_access(token_id, token_details):
    tokens = identity.token_driver()
    return {
        'token': {
            # replaced isoformat() with strftime to make tempest pass
            'expires': datetime.datetime.fromtimestamp(
                tokens.expires(token_details)).strftime('%Y-%m-%dT%H:%M:%SZ'),
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
        username = utils.lookup(creds,
                                'auth',
                                'passwordCredentials',
                                'username')
        credential = utils.lookup(creds,
                                  'auth',
                                  'passwordCredentials',
                                  'password')
        token_id = utils.lookup(creds, 'auth', 'token', 'id')
        token_driver = identity.token_driver()
        token_auth = None
        if token_id:
            token = identity.token_id_driver().token_from_id(token_id)
            token_driver.validate_token(token)
            username = token_driver.username(token)
            credential = token_driver.credential(token)
            token_auth = token['auth_type'] == 'token'

        def assert_tenant(user):
            tenant = (utils.lookup(creds, 'auth', 'tenantId')
                      or utils.lookup(creds, 'auth', 'tenantName'))
            if tenant and str(user['accountId']) != tenant:
                raise exceptions.Unauthorized(
                    'Invalid username, password or tenant id')

        endpoint = cfg.CONF['softlayer']['endpoint']
        proxy = cfg.CONF['softlayer']['proxy']
        # If the 'password' is the right length, treat it as an API api_key
        if len(credential) == 64:
            client = SoftLayer.Client(username=username,
                                      api_key=credential,
                                      endpoint_url=endpoint,
                                      proxy=proxy)
            user = client['Account'].getCurrentUser(mask=USER_MASK)
            assert_tenant(user)
            return {'user': user, 'credential': credential,
                    'auth_type': 'api_key'}

        else:
            client = SoftLayer.Client(endpoint_url=endpoint,
                                      proxy=proxy)
            client.auth = None
            try:
                if token_auth:
                    client.auth = SoftLayer.TokenAuthentication(
                        token['user_id'], credential)
                else:
                    userId, tokenHash = (
                        client.authenticate_with_password(username, credential)
                    )

                user = client['Account'].getCurrentUser(mask=USER_MASK)
                assert_tenant(user)

                if token_auth:
                    tokenHash = credential

                return {'user': user, 'credential': tokenHash,
                        'auth_type': 'token'}
            except SoftLayer.SoftLayerAPIError as e:
                if (e.faultCode == "SoftLayer_Exception_User_Customer"
                        "_LoginFailed"):
                    raise exceptions.Unauthorized(e.faultString)
                raise


class NoAuthDriver(identity.AuthDriver):
    """Auto-approve an identity request to a single default SL credential.

    Validates a consumer's identity in the jumpgate.conf and grants the
    consumer eligibility for an authentication token.
    """

    def __init__(self):
        super(NoAuthDriver, self).__init__()

    def authenticate(self, creds):
        """Performs faux authentication

        :param creds: The credentials in dict form as passed to the API
        in a request to authenticate and obtain a new token.  Not used,
        but present for parent-class compatibility.
        """

        endpoint = cfg.CONF['softlayer']['endpoint']
        proxy = cfg.CONF['softlayer']['proxy']
        default_user = cfg.CONF['softlayer']['noauth_user']
        default_api_key = cfg.CONF['softlayer']['noauth_api_key']
        client = SoftLayer.Client(username=default_user,
                                  api_key=default_api_key,
                                  endpoint_url=endpoint,
                                  proxy=proxy)
        user = client['Account'].getCurrentUser(mask=USER_MASK)
        return {'user': user, 'credential': default_api_key,
                'auth_type': 'api_key'}


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

    def _add_catalog_to_access(self, access, token):
        tokens = identity.token_driver()
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

    def on_post(self, req, resp):
        body = req.stream.read().decode()
        credentials = json.loads(body)
        tokens = identity.token_driver()

        auth = identity.auth_driver().authenticate(credentials)
        if auth is None:
            raise exceptions.Unauthorized('Unauthorized credentials')
        token = tokens.create_token(credentials, auth)
        tok_id = identity.token_id_driver().create_token_id(token)
        access = get_access(tok_id, token)

        # Add catalog to the access data
        self._add_catalog_to_access(access, token)

        resp.status = 200
        resp.body = {'access': access}

    def on_get(self, req, resp, token_id):
        tokens = identity.token_driver()
        token = identity.token_id_driver().token_from_id(token_id)
        identity.token_driver().validate_token(token)
        raw_endpoints = self._get_catalog(tokens.tenant_id(token),
                                          tokens.user_id(token))
        endpoints = []
        for services in raw_endpoints.values():
            for service_type, service in services.items():
                d = {
                    'adminURL': service.get('adminURL'),
                    'name': service.get('name', 'Unknown'),
                    'publicURL': service.get('publicURL'),
                    'privateURL': service.get('privateURL'),
                    'region': service.get('region', 'RegionOne'),
                    'tenantId': tokens.tenant_id(token),
                    'type': service_type,
                }
                endpoints.append(d)
        resp.status = 200
        resp.body = {'endpoints': endpoints, 'endpoints_links': []}


class TokenV2(TokensV2):
    def __init__(self, template_file):
        super(TokenV2, self).__init__(template_file)

    def on_get(self, req, resp, token_id):
        token = identity.token_id_driver().token_from_id(token_id)
        identity.token_driver().validate_access(token, tenant_id=req.get_param(
            'belongsTo'))
        access = get_access(token_id, token)

        # Add catalog to the access data
        self._add_catalog_to_access(access, token)

        resp.status = 200
        resp.body = {'access': access}

    def on_delete(self, req, resp, token_id):
        # This method is called when OpenStack wants to remove a token's
        # validity, such as when a cookie expires. Our login tokens can't
        # be forced to expire yet, so this does nothing.
        LOG.warning('User attempted to delete token: %s', token_id)
        resp.status = 202
        resp.body = ''


class FakeTokenIdDriver(identity.TokenIdDriver):
    """Fake 'accept-anything' Jumpgate token ID driver

    All token ids map to a single Softlayer user/tenant.
    This is meant for environments that use a separate 'real' keystone
    and want to just have any token be accepted andmap to a single
    SoftLayer user/tenant, defined in the jumpgate.conf.
    """

    def __init__(self):
        super(FakeTokenIdDriver, self).__init__()

    def create_token_id(self, token):
        # Doesn't matter how we encode, since decode will always give
        # same result no matter what input, but for now do the same as our
        # default driver
        return base64.b64encode(aes.encode_aes(json.dumps(token)))

    def token_from_id(self, token_id):
        try:
            tokens = identity.token_driver()
            if (identity.auth_driver().__class__.__name__ != "NoAuthDriver"):
                raise exceptions.InvalidTokenError(
                    'Auth-driver must be NoAuthDriver')
            auth = identity.auth_driver().authenticate(None)
            if auth is None:
                raise exceptions.Unauthorized('Unauthorized credentials')
            token = tokens.create_token(None, auth)
            return token
        except (TypeError, ValueError):
            raise exceptions.InvalidTokenError('Malformed token')
