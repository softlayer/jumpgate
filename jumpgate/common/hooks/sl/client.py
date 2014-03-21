from SoftLayer import Client
from oslo.config import cfg
from jumpgate.common.hooks import request_hook
from jumpgate.common.sl.auth import get_auth


@request_hook(True)
def bind_client(req, resp, kwargs):
    client = Client(endpoint_url=cfg.CONF['softlayer']['endpoint'],
                    proxy=cfg.CONF['softlayer']['proxy'])
    client.auth = None
    req.env['sl_client'] = client

    auth_token = req.env.get('auth', None)

    if auth_token is not None:
        client.auth = get_auth(auth_token)
