from jumpgate.baremetal.drivers.sl import nodes
from jumpgate.common import sl


def setup_routes(app, disp):
    # V1 Routes
    disp.set_handler('v1_nodes', nodes.NodesV1())

    sl.add_hooks(app)
