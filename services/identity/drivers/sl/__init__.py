import falcon
from SoftLayer import Client, TokenAuthentication
from services.identity import identity_dispatcher
from .endpoints.index import SLIdentityV2Index
from .endpoints.tenants import SLIdentityV2Tenants
from .endpoints.tokens import SLIdentityV2Tokens
from services.common.babelfish import before_hooks

# Set handlers for the routes we support

# V3 Routes
# None currently supported

# V2 Routes
identity_dispatcher.set_handler('v2_index', SLIdentityV2Index())
identity_dispatcher.set_handler('v2_tenants', SLIdentityV2Tenants())
identity_dispatcher.set_handler('v2_tokens', SLIdentityV2Tokens())

# Don't forget to import the routes or else nothing will happen.
identity_dispatcher.import_routes()

#print(identity_dispatcher.get_unused_endpoints())


# TODO - This probably needs to be made into a generic process that other
# drivers can hook into.
def get_client(req, resp, kwargs):
    client = Client()
    tenant_id = None

    if req.headers.get('x-auth-token'):
        (userId, hash) = req.headers['x-auth-token'].split(':')

        auth = TokenAuthentication(userId, hash)
        client = Client(auth=auth)

        account = client['Account'].getObject()
        tenant_id = str(account['id'])

    api = identity_dispatcher.get_api()
    api.config['sl_client'] = client
    api.current_tenant_id = tenant_id

before_hooks.append(get_client)
