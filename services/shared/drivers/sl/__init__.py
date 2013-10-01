from SoftLayer import Client, TokenAuthentication

from services.common.babelfish import before_hooks


def get_client(req, resp, kwargs):
    client = Client()
    client.auth = None
    req.env['tenant_id'] = None

    if req.headers.get('x-auth-token'):
        (userId, hash) = req.headers['x-auth-token'].split(':')

        auth = TokenAuthentication(userId, hash)
        client.auth = auth

        account = client['Account'].getObject()
        req.env['tenant_id'] = str(account['id'])

    req.env['sl_client'] = client

before_hooks.append(get_client)
