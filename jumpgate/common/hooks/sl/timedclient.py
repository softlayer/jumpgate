import time

from oslo.config import cfg
import SoftLayer

from jumpgate.common import hooks
from jumpgate.common.sl import auth


@hooks.request_hook(True)
def bind_client(req, resp, kwargs):
    req.env['sl_timehook_start_time'] = time.time()
    endpoint = cfg.CONF['softlayer']['endpoint']
    client = SoftLayer.TimedClient(endpoint_url=endpoint,
                                   proxy=cfg.CONF['softlayer']['proxy'])
    client.auth = None
    req.env['sl_client'] = client

    auth_token = req.env.get('auth', None)

    if auth_token is not None:
        client.auth = auth.get_auth(auth_token)
