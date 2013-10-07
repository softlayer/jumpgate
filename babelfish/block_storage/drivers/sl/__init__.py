from babelfish.block_storage import storage_dispatcher
from .endpoints.volumes import SLBlockStorageV2Volumes

# Set handlers for the routes we support

# V2 Routes
storage_dispatcher.set_handler('v2_volumes', SLBlockStorageV2Volumes())
storage_dispatcher.set_handler('v2_os_volumes', SLBlockStorageV2Volumes())

# Don't forget to import the routes or else nothing will happen.
storage_dispatcher.import_routes()

#print(block_storage_dispatcher.get_unused_endpoints())
