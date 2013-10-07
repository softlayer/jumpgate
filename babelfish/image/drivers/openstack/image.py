from babelfish.image import image_dispatcher
from babelfish.shared.drivers.openstack.responder import OpenStackResponder

responder = OpenStackResponder()

for endpoint in image_dispatcher.get_unused_endpoints():
    image_dispatcher.set_handler(endpoint, responder)

# Don't forget to import the routes or else nothing will happen.
image_dispatcher.import_routes()
