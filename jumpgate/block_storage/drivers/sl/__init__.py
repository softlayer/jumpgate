from .endpoints.volumes import VolumesV2


def get_dispatcher(app, disp):
    # V2 Routes
    disp.set_handler('v2_volumes', VolumesV2())
    disp.set_handler('v2_os_volumes', VolumesV2())
