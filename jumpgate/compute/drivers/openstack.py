from jumpgate.common.openstack.responder import setup_responder


def setup_routes(app, disp):
    return setup_responder(app, disp, 'compute')
