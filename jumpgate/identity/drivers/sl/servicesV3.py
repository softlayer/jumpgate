import datetime
import logging
import json
import base64

from jumpgate.common.sl.auth import get_new_token, get_token_details, get_auth
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

class ServicesV3(object):
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
    def on_get(self, req, resp):
        client = req.env['sl_client']
        account = client['Account'].getObject()

        tenants = [
            {
                'enabled': True,
                'description': None,
                'name': str(account['id']),
                'id': str(account['id']),
            },
        ]
        
        # Add catalog to the access data
        raw_catalog = self._get_catalog(account['id'], account['id'])
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

        resp.body = catalog
