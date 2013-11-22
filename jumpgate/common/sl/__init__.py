from SoftLayer import Client, API_PUBLIC_ENDPOINT
from oslo.config import cfg

from jumpgate.common.sl.auth import get_auth


opts = [
    cfg.StrOpt('endpoint', default=API_PUBLIC_ENDPOINT),
    cfg.StrOpt('catalog_template_file', default='identity.templates'),
]

cfg.CONF.register_opts(opts, group='softlayer')


def hook_get_client(req, resp, kwargs):
    client = Client(endpoint_url=cfg.CONF['softlayer']['endpoint'])
    client.auth = None
    req.env['tenant_id'] = None

    if req.headers.get('x-auth-token'):
        auth, token, _ = get_auth(req, resp)
        client.auth = auth

        account_id = kwargs.get('tenant_id')
        if not account_id:
            account = client['Account'].getObject()
            account_id = str(account['id'])
        req.env['tenant_id'] = account_id

    req.env['sl_client'] = client


def add_hooks(app):
    if hook_get_client not in app.before_hooks:
        app.before_hooks.append(hook_get_client)
