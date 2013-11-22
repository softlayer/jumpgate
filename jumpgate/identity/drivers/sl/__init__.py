from .tenants import TenantsV2
from .tokens import TokensV2, TokenV2
from jumpgate.common.sl import add_hooks


def setup_routes(app, disp):
    # V3 Routes
    # None currently supported

    # V2 Routes
    disp.set_handler('v2_tenants', TenantsV2())
    disp.set_handler('v2_tokens', TokensV2(app))
    disp.set_handler('v2_token', TokenV2())

    add_hooks(app)
