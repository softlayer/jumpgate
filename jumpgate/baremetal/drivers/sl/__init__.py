from jumpgate.baremetal import dispatcher
from .nodes import NodesV1

# Set handlers for the routes we support

# V1 Routes
dispatcher.set_handler('v1_nodes', NodesV1())

# Don't forget to import the routes or else nothing will happen.
dispatcher.import_routes()
