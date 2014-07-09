from oslo.config import cfg
import SoftLayer

from jumpgate.common import hooks
from jumpgate.common.sl import auth


@hooks.request_hook(True)
def bind_client(req, resp, kwargs):
    extra_args = {}
    if SoftLayer.__version__ > 'v3.0.3':
        extra_args['proxy'] = cfg.CONF['softlayer']['proxy']

    endpoint = cfg.CONF['softlayer']['endpoint']
    client = SoftLayer.Client(endpoint_url=endpoint, **extra_args)
    client.auth = None
    req.env['sl_client'] = client

    auth_token = req.env.get('auth', None)

    if auth_token is not None:
        client.auth = auth.get_auth(auth_token)
