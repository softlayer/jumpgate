from jumpgate.common import sl as sl_common
from jumpgate.volume.drivers.sl import volumes


def setup_routes(app, disp):
    # V2 Routes
    disp.set_handler('v2_volumes', volumes.VolumesV2())
    disp.set_handler('v2_os_volumes', volumes.VolumesV2())
    disp.set_handler('v2_volumes_detail', volumes.VolumesV2())

    # V1 Routes
    disp.set_handler('v1_volumes_detail', volumes.VolumesV1())
    disp.set_handler('v1_volume', volumes.VolumeV1())
    disp.set_handler('v1_volumes', volumes.VolumesV1())

    sl_common.add_hooks(app)
