from jumpgate.network import network_dispatcher
from .endpoints.subnets import SubnetsV2
from .endpoints.networks import NetworksV2

# Set handlers for the routes we support

# V2 Routes
network_dispatcher.set_handler('v2_networks', NetworksV2())
network_dispatcher.set_handler('v2_subnets', SubnetsV2())

# Don't forget to import the routes or else nothing will happen.
network_dispatcher.import_routes()
