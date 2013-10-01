from services.image import image_dispatcher
from .endpoints.images import SLImageV1Image, SLImageV1Images

# Set handlers for the routes we support

# V1 Routes
image_dispatcher.set_handler('v1_image', SLImageV1Image())
image_dispatcher.set_handler('v1_images', SLImageV1Images())
image_dispatcher.set_handler('v1_images_detail', SLImageV1Images())

# V2 Routes
image_dispatcher.set_handler('v2_image', SLImageV1Image())
image_dispatcher.set_handler('v2_images', SLImageV1Images())
image_dispatcher.set_handler('v2_images_detail', SLImageV1Images())


# Don't forget to import the routes or else nothing will happen.
image_dispatcher.import_routes()
