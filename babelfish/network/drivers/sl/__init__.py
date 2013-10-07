from babelfish.network import network_dispatcher
from .endpoints.subnets import SLNetworkV2Subnets
from .endpoints.networks import SLNetworkV2Networks

# Set handlers for the routes we support

# V2 Routes
network_dispatcher.set_handler('v2_networks', SLNetworkV2Networks())
network_dispatcher.set_handler('v2_subnets', SLNetworkV2Subnets())

# Don't forget to import the routes or else nothing will happen.
network_dispatcher.import_routes()
