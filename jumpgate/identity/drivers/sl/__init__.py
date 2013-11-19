from .endpoints.tenants import TenantsV2
from .endpoints.tokens import TokensV2, TokenV2


def setup(app, disp):
    # V3 Routes
    # None currently supported

    # V2 Routes
    disp.set_handler('v2_tenants', TenantsV2())
    disp.set_handler('v2_tokens', TokensV2(app))
    disp.set_handler('v2_token', TokenV2())
