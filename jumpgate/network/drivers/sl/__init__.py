from .subnets import SubnetV2, SubnetsV2
from .networks import NetworkV2, NetworksV2
from .extensions import ExtensionsV2
from jumpgate.common.sl import add_hooks


def setup_routes(app, disp):
    # V2 Routes
    disp.set_handler('v2_network', NetworkV2())
    disp.set_handler('v2_networks', NetworksV2())
    disp.set_handler('v2_subnet', SubnetV2())
    disp.set_handler('v2_subnets', SubnetsV2())
    disp.set_handler('v2_extensions', ExtensionsV2())

    add_hooks(app)
