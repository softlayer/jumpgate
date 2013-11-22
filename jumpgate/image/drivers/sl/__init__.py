from .images import ImageV1, ImagesV1, SchemaImageV2, SchemaImagesV2, ImagesV2
from jumpgate.common.sl import add_hooks


def setup_routes(app, disp):
    # V2 Routes
    disp.set_handler('v2_image', ImageV1(app))
    disp.set_handler('v2_images', ImagesV2(app))
    disp.set_handler('v2_images_detail', ImagesV2(app))
    disp.set_handler('v2_schema_image', SchemaImageV2())
    disp.set_handler('v2_schema_images', SchemaImagesV2())

    # V1 Routes
    disp.set_handler('v1_image', ImageV1(app))
    disp.set_handler('v1_images', ImagesV1(app))
    disp.set_handler('v1_images_detail', ImagesV1(app))

    add_hooks(app)
