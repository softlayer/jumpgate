from jumpgate.common.openstack.responder import setup_responder


def setup_driver(app, disp):
    return setup_responder(app, disp)
