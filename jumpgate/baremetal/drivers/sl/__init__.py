from .nodes import NodesV1

from jumpgate.common.sl import add_hooks


def setup_routes(app, disp):
    # V1 Routes
    disp.set_handler('v1_nodes', NodesV1())

    add_hooks(app)
