import os.path

from jumpgate.common import sl as sl_common
from jumpgate.identity.drivers.sl import auth_tokens_v3
from jumpgate.identity.drivers.sl import services_v3
from jumpgate.identity.drivers.sl import tenants
from jumpgate.identity.drivers.sl import tokens
from jumpgate.identity.drivers.sl import user
from jumpgate.identity.drivers.sl import user_projects_v3
from jumpgate.identity.drivers.sl import v3
from jumpgate.identity.drivers.sl import versions


def setup_routes(app, disp):
    # V3 Routes
    disp.set_handler('v3_auth_index', v3.V3(disp))
    disp.set_handler('v3_user_projects', user_projects_v3.UserProjectsV3())

    template_file = app.config.softlayer.catalog_template_file
    if not os.path.exists(template_file):
        template_file = app.config.find_file(template_file)

    if template_file is None:
        raise ValueError('Template file not found')

    template_file_v3 = app.config.softlayer.catalog_template_file_v3
    if not os.path.exists(template_file_v3):
        template_file_v3 = app.config.find_file(template_file_v3)

    if template_file_v3 is None:
        raise ValueError('Template file v3 not found')

    # V2 Routes
    disp.set_handler('v2_tenants', tenants.TenantsV2())
    disp.set_handler('v2_token', tokens.TokenV2(template_file))
    disp.set_handler('v2_user', user.UserV2())

    disp.set_handler('versions', versions.Versions(disp))

    disp.set_handler('v2_tokens', tokens.TokensV2(template_file))
    disp.set_handler('v2_token_endpoints', tokens.TokensV2(template_file))

    # V3 auth token route
    disp.set_handler('v3_auth_tokens',
                     auth_tokens_v3.AuthTokensV3(template_file_v3))

    # V3 service
    disp.set_handler('v3_services', services_v3.ServicesV3(template_file_v3))

    sl_common.add_hooks(app)
