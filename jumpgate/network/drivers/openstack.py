from jumpgate.common import openstack


def setup_routes(app, disp):
    return openstack.setup_responder(app, disp, 'network')
