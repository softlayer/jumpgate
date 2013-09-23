from services.image import image_dispatcher
from .endpoints.images import SLImageV1Image

# Set handlers for the routes we support

# V2 Routes
image_dispatcher.set_handler('v1_image', SLImageV1Image())

# Don't forget to import the routes or else nothing will happen.
image_dispatcher.import_routes()
