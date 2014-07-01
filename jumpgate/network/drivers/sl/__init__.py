from jumpgate.common import sl as sl_common
from jumpgate.network.drivers.sl import extensions
from jumpgate.network.drivers.sl import networks
from jumpgate.network.drivers.sl import subnets


def setup_routes(app, disp):
    # V2 Routes
    disp.set_handler('v2_network', networks.NetworkV2())
    disp.set_handler('v2_networks', networks.NetworksV2())
    disp.set_handler('v2_subnet', subnets.SubnetV2())
    disp.set_handler('v2_subnets', subnets.SubnetsV2())
    disp.set_handler('v2_extensions', extensions.ExtensionsV2())

    sl_common.add_hooks(app)
