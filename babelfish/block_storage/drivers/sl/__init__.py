from babelfish.block_storage import storage_dispatcher
from .endpoints.volumes import VolumesV2

# Set handlers for the routes we support

# V2 Routes
storage_dispatcher.set_handler('v2_volumes', VolumesV2())
storage_dispatcher.set_handler('v2_os_volumes', VolumesV2())

# Don't forget to import the routes or else nothing will happen.
storage_dispatcher.import_routes()

#print(block_storage_dispatcher.get_unused_endpoints())
