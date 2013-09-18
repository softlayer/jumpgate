from services.identity import identity_dispatcher
from .endpoints.index import SLIdentityIndex
from .endpoints.tokens import SLIdentityTokens

# Set handlers for the routes we support
identity_dispatcher.set_handler('v3_index', SLIdentityIndex())
identity_dispatcher.set_handler('v3_tokens', SLIdentityTokens())

# Don't forget to import the routes or else nothing will happen.
identity_dispatcher.import_routes()

print(identity_dispatcher.get_unused_endpoints())
