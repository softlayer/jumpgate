import datetime
import logging
import json
import base64

from jumpgate.common.sl.auth import get_new_token_v3, get_token_details, get_auth
from jumpgate.common.aes import encode_aes

from SoftLayer import Client
from oslo.config import cfg

LOG = logging.getLogger(__name__)


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
    
    
def get_access_v3(token_id, token_details, user):
    return {
        'token': {
            'expires_at': datetime.datetime.fromtimestamp(
                token_details['expires']).isoformat(),
        'issued_at': datetime.datetime.fromtimestamp(
                token_details['expires']).isoformat(),
            'methods':['password'],
        },
        'user': {
            'id': user['id'],
            'links': [0],
            'name': user['username'],
        },
    }


class AuthTokensV3(object):
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
        token_details, user = get_new_token_v3(credentials)
        token_id = base64.b64encode(encode_aes(json.dumps(token_details)))

        access = get_access_v3(token_id, token_details, user)
        
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

        access['Catalog'] = catalog

        resp.status = 200
        #resp.body = {'access': access}

        resp.status = 200
        resp.set_header('X-Subject-Token',str(token_id))
        resp.body = access


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
