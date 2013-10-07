from SoftLayer import Client

from babelfish.api import app
from babelfish.shared.drivers.sl.auth import get_auth
import logging
logger = logging.getLogger(__name__)


def get_client(req, resp, kwargs):
    client = Client()
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

app.before_hooks.append(get_client)
