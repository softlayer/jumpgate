import datetime
import logging

from SoftLayer import Client

from jumpgate.common.sl.errors import convert_errors
from jumpgate.common.sl.auth import get_auth
from jumpgate.config import CONF

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


class TokensV2(object):
    def __init__(self, template_file):
        self._load_templates(template_file)

    def _load_templates(self, template_file):
        try:
            self.templates = parse_templates(open(template_file))
        except IOError:
            LOG.critical('Unable to open template file %s' % template_file)
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

    @convert_errors
    def on_post(self, req, resp):
        body = req.stream.read().decode()
        auth, token, err = get_auth(req, resp, body=body)
        if err:
            return err
        client = Client(auth=auth, endpoint_url=CONF['softlayer']['endpoint'])

        user = client['Account'].getCurrentUser(mask='id, account, username')
        account = user['account']

        raw_catalog = self._get_catalog(account['id'], user['id'])
        catalog = []
        for region, services in raw_catalog.items():
            for service_type, service in services.items():
                d = {
                    'type': service_type,
                    'name': service.get('name', 'Unknown'),
                    'endpoints': [{
                        'region': service.get('region', 'RegionOne'),
                        'publicURL': service.get('publicURL'),
                        'privateURL': service.get('privateURL'),
                    }],
                    'endpoint_links': [],
                }
                catalog.append(d)

        # Set expiration for a day
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
            'serviceCatalog': catalog,
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
