from jumpgate.common.openstack import setup_responder


def setup_routes(app, disp):
    return setup_responder(app, disp, 'baremetal')
