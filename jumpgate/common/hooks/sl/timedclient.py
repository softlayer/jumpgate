from SoftLayer import TimedClient
from oslo.config import cfg
from jumpgate.common.hooks import request_hook
from jumpgate.common.sl.auth import get_auth
import time


@request_hook(True)
def bind_client(req, resp, kwargs):
    req.env['sl_timehook_start_time'] = time.time()
    client = TimedClient(endpoint_url=cfg.CONF['softlayer']['endpoint'],
                         proxy=cfg.CONF['softlayer']['proxy'])
    client.auth = None
    req.env['sl_client'] = client

    auth_token = req.env.get('auth', None)

    if auth_token is not None:
        client.auth = get_auth(auth_token)
