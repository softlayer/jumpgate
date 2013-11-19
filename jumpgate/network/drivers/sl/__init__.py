from .endpoints.subnets import SubnetsV2
from .endpoints.networks import NetworksV2


def setup(app, disp):
    # V2 Routes
    disp.set_handler('v2_networks', NetworksV2())
    disp.set_handler('v2_subnets', SubnetsV2())
