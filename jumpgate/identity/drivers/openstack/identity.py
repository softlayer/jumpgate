from jumpgate.identity import identity_dispatcher
from jumpgate.shared.drivers.openstack.responder import OpenStackResponder

responder = OpenStackResponder()

for endpoint in identity_dispatcher.get_unused_endpoints():
    identity_dispatcher.set_handler(endpoint, responder)

# Don't forget to import the routes or else nothing will happen.
identity_dispatcher.import_routes()
