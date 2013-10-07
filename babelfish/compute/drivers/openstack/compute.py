from babelfish.compute import compute_dispatcher
from babelfish.shared.drivers.openstack.responder import OpenStackResponder

responder = OpenStackResponder()

for endpoint in compute_dispatcher.get_unused_endpoints():
    compute_dispatcher.set_handler(endpoint, responder)

# Don't forget to import the routes or else nothing will happen.
compute_dispatcher.import_routes()
