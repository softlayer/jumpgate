from jumpgate.shared.drivers.openstack.responder import setup_responder


def setup(app, disp):
    return setup_responder(app, disp)
