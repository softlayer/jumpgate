from jumpgate.identity import identity_dispatcher
from .endpoints.tenants import TenantsV2
from .endpoints.tokens import TokensV2, TokenV2

# Set handlers for the routes we support


# V3 Routes
# None currently supported

# V2 Routes
identity_dispatcher.set_handler('v2_tenants', TenantsV2())
identity_dispatcher.set_handler('v2_tokens', TokensV2())
identity_dispatcher.set_handler('v2_token', TokenV2())

# Don't forget to import the routes or else nothing will happen.
identity_dispatcher.import_routes()

#print(identity_dispatcher.get_unused_endpoints())
