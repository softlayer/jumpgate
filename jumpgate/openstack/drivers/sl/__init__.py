from jumpgate.openstack import openstack_dispatcher
from .endpoints.index import IndexV2

# Set handlers for the routes we support

# V3 Routes
# None currently supported

# V2 Routes
openstack_dispatcher.set_handler('main_index', IndexV2())
openstack_dispatcher.set_handler('v2_index', IndexV2())

# Don't forget to import the routes or else nothing will happen.
openstack_dispatcher.import_routes()

#print(openstack_dispatcher.get_unused_endpoints())
