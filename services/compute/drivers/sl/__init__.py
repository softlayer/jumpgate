from services.compute import compute_dispatcher
from .endpoints.flavors import SLComputeV2Flavor, SLComputeV2Flavors
from .endpoints.limits import SLComputeV2Limits
from .endpoints.servers import (SLComputeV2Server, SLComputeV2Servers,
                                SLComputeV2ServersDetail)
from .endpoints.usage import SLComputeV2Usage

# Set handlers for the routes we support

# V2 Routes
flavor = SLComputeV2Flavor()
flavors = SLComputeV2Flavors()

compute_dispatcher.set_handler('v2_flavor', flavor)
compute_dispatcher.set_handler('v2_flavors', flavors)
compute_dispatcher.set_handler('v2_flavors_detail', flavors)
compute_dispatcher.set_handler('v2_tenant_flavor', flavor)
compute_dispatcher.set_handler('v2_tenant_flavors', flavors)
compute_dispatcher.set_handler('v2_tenant_flavors_detail', flavors)
compute_dispatcher.set_handler('v2_limits', SLComputeV2Limits())
compute_dispatcher.set_handler('v2_server', SLComputeV2Server())
compute_dispatcher.set_handler('v2_servers', SLComputeV2Servers())
compute_dispatcher.set_handler('v2_servers_detail', SLComputeV2ServersDetail())
compute_dispatcher.set_handler('v2_tenant_usage', SLComputeV2Usage())

# Don't forget to import the routes or else nothing will happen.
compute_dispatcher.import_routes()

#print(compute_dispatcher.get_unused_endpoints())
