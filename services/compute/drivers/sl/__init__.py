from SoftLayer import Client, TokenAuthentication

from services.compute import compute_dispatcher
from .endpoints.flavors import SLComputeV2Flavor, SLComputeV2Flavors
from .endpoints.limits import SLComputeV2Limits
from .endpoints.servers import SLComputeV2Server, SLComputeV2Servers

# Set handlers for the routes we support

# V2 Routes
compute_dispatcher.set_handler('v2_flavor', SLComputeV2Flavor)
compute_dispatcher.set_handler('v2_flavos', SLComputeV2Flavors)
compute_dispatcher.set_handler('v2_limits', SLComputeV2Limits)
compute_dispatcher.set_handler('v2_server', SLComputeV2Server)
compute_dispatcher.set_handler('v2_servers', SLComputeV2Servers())

# Don't forget to import the routes or else nothing will happen.
compute_dispatcher.import_routes()

#print(compute_dispatcher.get_unused_endpoints())
