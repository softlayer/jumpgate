import os.path

from .user import UserV2
from .tenants import TenantsV2
from .tokens import TokensV2, TokenV2
from .versions import Versions
from jumpgate.common.sl import add_hooks


def setup_routes(app, disp):
    # V3 Routes
    # None currently supported

    # V2 Routes
    disp.set_handler('v2_tenants', TenantsV2())
    disp.set_handler('v2_token', TokenV2())
    disp.set_handler('versions', Versions(disp))
    disp.set_handler('v2_user', UserV2())

    template_file = app.config.softlayer.catalog_template_file
    if not os.path.exists(template_file):
        template_file = app.config.find_file(template_file)

    if template_file is None:
        raise ValueError('Template file not found')

    disp.set_handler('v2_tokens', TokensV2(template_file))

    add_hooks(app)
