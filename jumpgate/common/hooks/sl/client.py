import SoftLayer
from oslo.config import cfg
from jumpgate.common.hooks import request_hook
from jumpgate.common.sl.auth import get_auth


@request_hook(True)
def bind_client(req, resp, kwargs):
    extra_args = {}
    if SoftLayer.__version__ > 'v3.0.3':
        extra_args['proxy'] = cfg.CONF['softlayer']['proxy']

    client = SoftLayer.Client(endpoint_url=cfg.CONF['softlayer']['endpoint'],
                              **extra_args)
    client.auth = None
    req.env['sl_client'] = client

    auth_token = req.env.get('auth', None)

    if auth_token is not None:
        client.auth = get_auth(auth_token)
