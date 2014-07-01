from oslo.config import cfg
import SoftLayer

from jumpgate.common.sl import auth
from jumpgate.common.sl import errors

opts = [
    cfg.StrOpt('endpoint', default=SoftLayer.API_PUBLIC_ENDPOINT),
    cfg.StrOpt('catalog_template_file', default='identity.templates'),
    cfg.StrOpt('catalog_template_file_v3', default='identity_v3.templates'),
]

cfg.CONF.register_opts(opts, group='softlayer')


def hook_get_client(req, resp, kwargs):
    endpoint = cfg.CONF['softlayer']['endpoint']
    client = SoftLayer.Client(endpoint_url=endpoint)
    client.auth = None
    req.env['tenant_id'] = None

    if req.headers.get('X-AUTH-TOKEN'):
        if 'X-AUTH-TOKEN' in req.headers:
            tenant_id = kwargs.get('tenant_id',
                                   req.headers.get('X-AUTH-PROJECT-ID'))
            token_details = auth.get_token_details(req.headers['X-AUTH-TOKEN'],
                                                   tenant_id=tenant_id)

            client.auth = auth.get_auth(token_details)

            req.env['tenant_id'] = token_details['tenant_id']

    req.env['sl_client'] = client


def add_hooks(app):
    if hook_get_client not in app.before_hooks:
        app.before_hooks.append(hook_get_client)

    app.add_error_handler(SoftLayer.SoftLayerAPIError,
                          errors.handle_softlayer_errors)
