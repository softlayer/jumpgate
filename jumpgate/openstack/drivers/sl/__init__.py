from .index import IndexV2


def setup_driver(app, disp):
    # V3 Routes
    # None currently supported

    # V2 Routes
    disp.set_handler('main_index', IndexV2(app))
    disp.set_handler('v2_index', IndexV2(app))
