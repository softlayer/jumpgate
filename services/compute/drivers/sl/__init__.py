from SoftLayer import Client, TokenAuthentication

from services.compute import compute_dispatcher
from .endpoints.servers import SLComputeV2Servers

# Set handlers for the routes we support

# V2 Routes
compute_dispatcher.set_handler('v2_servers', SLComputeV2Servers())

# Don't forget to import the routes or else nothing will happen.
compute_dispatcher.import_routes()

#print(compute_dispatcher.get_unused_endpoints())


def get_client(req):
    client = Client()

    if req.headers.get('x-auth-token'):
        (userId, hash) = req.headers['x-auth-token'].split(':')

        auth = TokenAuthentication(userId, hash)
        client = Client(auth=auth)

    return client
