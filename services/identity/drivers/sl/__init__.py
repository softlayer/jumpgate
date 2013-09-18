from services.identity import identity_dispatcher
from .endpoints.index import SLIdentityIndex

identity_dispatcher.set_handler('index_v3', SLIdentityIndex())

identity_dispatcher.import_routes()
