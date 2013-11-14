from jumpgate.block_storage import storage_dispatcher
from jumpgate.shared.drivers.openstack.responder import OpenStackResponder

responder = OpenStackResponder()

for endpoint in storage_dispatcher.get_unused_endpoints():
    storage_dispatcher.set_handler(endpoint, responder)

# Don't forget to import the routes or else nothing will happen.
storage_dispatcher.import_routes()
