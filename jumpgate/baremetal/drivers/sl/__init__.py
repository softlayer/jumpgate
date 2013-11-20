from .nodes import NodesV1


def setup_driver(app, disp):
    # V1 Routes
    disp.set_handler('v1_nodes', NodesV1())
