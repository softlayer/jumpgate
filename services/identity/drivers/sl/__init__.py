from services.identity import identity_dispatcher
from .endpoints.index import SLIdentityV2Index
from .endpoints.tenants import SLIdentityV2Tenants
from .endpoints.tokens import SLIdentityV2Tokens, SLIdentityV2Token

# Set handlers for the routes we support

# V3 Routes
# None currently supported

# V2 Routes
identity_dispatcher.set_handler('v2_index', SLIdentityV2Index())
identity_dispatcher.set_handler('v2_tenants', SLIdentityV2Tenants())
identity_dispatcher.set_handler('v2_tokens', SLIdentityV2Tokens())
identity_dispatcher.set_handler('v2_token', SLIdentityV2Token())

# Don't forget to import the routes or else nothing will happen.
identity_dispatcher.import_routes()

#print(identity_dispatcher.get_unused_endpoints())
