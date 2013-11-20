from .subnets import SubnetsV2
from .networks import NetworksV2


def setup_driver(app, disp):
    # V2 Routes
    disp.set_handler('v2_networks', NetworksV2())
    disp.set_handler('v2_subnets', SubnetsV2())
