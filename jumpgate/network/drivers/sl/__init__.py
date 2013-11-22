from .subnets import SubnetsV2
from .networks import NetworksV2
from jumpgate.common.sl import add_hooks


def setup_routes(app, disp):
    # V2 Routes
    disp.set_handler('v2_networks', NetworksV2())
    disp.set_handler('v2_subnets', SubnetsV2())

    add_hooks(app)
