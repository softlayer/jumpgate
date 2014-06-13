from .volumes import VolumesV2, VolumesV1, VolumeV1
from jumpgate.common.sl import add_hooks


def setup_routes(app, disp):
    # V2 Routes
    disp.set_handler('v2_volumes', VolumesV2())
    disp.set_handler('v2_os_volumes', VolumesV2())
    disp.set_handler('v2_volumes_detail', VolumesV2())

    # V1 Routes
    disp.set_handler('v1_volumes_detail', VolumesV1())
    disp.set_handler('v1_volume', VolumeV1())
    disp.set_handler('v1_volumes', VolumesV1())

    add_hooks(app)
