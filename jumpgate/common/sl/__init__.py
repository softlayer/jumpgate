
from SoftLayer import Client, API_PUBLIC_ENDPOINT
from oslo.config import cfg

from jumpgate.common.sl.auth import get_auth, get_token_details
from jumpgate.common.sl.errors import handle_softlayer_errors
from SoftLayer import SoftLayerAPIError


opts = [
    cfg.StrOpt('endpoint', default=API_PUBLIC_ENDPOINT),
    cfg.StrOpt('catalog_template_file', default='identity.templates'),
    cfg.StrOpt('catalog_template_file_v3', default='identity.templates_v3'),
]

cfg.CONF.register_opts(opts, group='softlayer')


def hook_get_client(req, resp, kwargs):
    client = Client(endpoint_url=cfg.CONF['softlayer']['endpoint'])
    client.auth = None
    req.env['tenant_id'] = None

    if req.headers.get('X-AUTH-TOKEN'):
        if 'X-AUTH-TOKEN' in req.headers:
            tenant_id = kwargs.get('tenant_id',
                                   req.headers.get('X-AUTH-PROJECT-ID'))
            token_details = get_token_details(req.headers['X-AUTH-TOKEN'],
                                              tenant_id=tenant_id)

            client.auth = get_auth(token_details)

            req.env['tenant_id'] = token_details['tenant_id']

    req.env['sl_client'] = client


def add_hooks(app):
    if hook_get_client not in app.before_hooks:
        app.before_hooks.append(hook_get_client)

    app.add_error_handler(SoftLayerAPIError, handle_softlayer_errors)
