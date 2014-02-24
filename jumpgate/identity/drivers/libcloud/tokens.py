import json
import logging

from jumpgate.common.catalog import build_catalog, parse_templates
from jumpgate.common.libcloud.auth import get_new_token

LOG = logging.getLogger(__name__)


class TokensV2(object):
    def __init__(self, template_file):
        self.templates = {}
        self._load_templates(template_file)

    def on_post(self, req, resp):
        body = req.stream.read().decode()
        credentials = json.loads(body)
        token_details, user = get_new_token(credentials)
        token_id = base64.b64encode(encode_aes(json.dumps(token_details)))

#        access = get_access(token_id, token_details, user)

        # Add catalog to the access data
        raw_catalog = self._get_catalog(token_details['tenant_id'], user['id'])
        access['serviceCatalog'] = build_catalog(raw_catalog.values())

        resp.status = 200
        resp.body = {'access': access}

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

    def _load_templates(self, template_file):
        try:
            self.templates = parse_templates(open(template_file))
        except IOError:
            LOG.critical('Unable to open template file %s', template_file)
            raise
