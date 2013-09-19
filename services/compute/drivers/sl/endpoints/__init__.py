from SoftLayer import Client, TokenAuthentication


def get_client(req):
    client = Client()

    if req.headers.get('x-auth-token'):
        (userId, hash) = req.headers['x-auth-token'].split(':')

        auth = TokenAuthentication(userId, hash)
        client = Client(auth=auth)

    return client
