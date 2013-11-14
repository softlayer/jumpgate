from jumpgate.image import image_dispatcher
from jumpgate.shared.drivers.openstack.responder import OpenStackResponder

responder = OpenStackResponder()

for endpoint in image_dispatcher.get_unused_endpoints():
    image_dispatcher.set_handler(endpoint, responder)

# Don't forget to import the routes or else nothing will happen.
image_dispatcher.import_routes()
