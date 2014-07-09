from jumpgate.common import sl as sl_common
from jumpgate.image.drivers.sl import images


def setup_routes(app, disp):
    # V2 Routes
    disp.set_handler('v2_image', images.ImageV1(app))
    disp.set_handler('v2_images', images.ImagesV2(app))
    disp.set_handler('v2_images_detail', images.ImagesV2(app))
    disp.set_handler('v2_schema_image', images.SchemaImageV2())
    disp.set_handler('v2_schema_member', images.SchemaMemberV2())
    disp.set_handler('v2_schema_members', images.SchemaMembersV2())
    disp.set_handler('v2_schema_images', images.SchemaImagesV2())

    # V1 Routes
    disp.set_handler('v1_image', images.ImageV1(app))
    disp.set_handler('v1_images', images.ImagesV1(app))
    disp.set_handler('v1_images_detail', images.ImagesV1(app))

    sl_common.add_hooks(app)
