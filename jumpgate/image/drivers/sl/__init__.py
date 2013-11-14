from jumpgate.image import image_dispatcher
from .endpoints.images import (ImageV1, ImagesV1,
                               SchemaImageV2, SchemaImagesV2,
                               ImagesV2)

# Set handlers for the routes we support

# V2 Routes
image_dispatcher.set_handler('v2_image', ImageV1())
image_dispatcher.set_handler('v2_images', ImagesV2())
image_dispatcher.set_handler('v2_images_detail', ImagesV2())
image_dispatcher.set_handler('v2_schema_image', SchemaImageV2())
image_dispatcher.set_handler('v2_schema_images', SchemaImagesV2())
image_dispatcher.set_handler('v2_tenant_image', ImageV1())
image_dispatcher.set_handler('v2_tenant_images', ImagesV2())
image_dispatcher.set_handler('v2_tenant_images_detail', ImagesV2())

# V1 Routes
image_dispatcher.set_handler('v1_image', ImageV1())
image_dispatcher.set_handler('v1_images', ImagesV1())
image_dispatcher.set_handler('v1_images_detail', ImagesV1())

# Don't forget to import the routes or else nothing will happen.
image_dispatcher.import_routes()
