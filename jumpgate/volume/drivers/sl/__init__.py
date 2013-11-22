from .volumes import VolumesV2
from jumpgate.common.sl import add_hooks


def setup_routes(app, disp):
    # V2 Routes
    disp.set_handler('v2_volumes', VolumesV2())
    disp.set_handler('v2_os_volumes', VolumesV2())

    add_hooks(app)
