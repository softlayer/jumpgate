import os.path

from .tenants import TenantsV2
from .tokens import TokensV2, TokenV2
from .versions import Versions
from .v3 import V3
from .servicesV3 import ServicesV3
from .authTokensV3 import AuthTokensV3
from .userProjectsV3 import UserProjectsV3
from jumpgate.common.sl import add_hooks


def setup_routes(app, disp):
    # V3 Routes
    # 
    disp.set_handler('v3_auth_index',V3(disp))
    disp.set_handler('v3_user_projects', UserProjectsV3())
    
    

    # V2 Routes
    disp.set_handler('v2_tenants', TenantsV2())
    disp.set_handler('v2_token', TokenV2())
    disp.set_handler('versions', Versions(disp))

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

    disp.set_handler('v2_tokens', TokensV2(template_file))
    
    #V3 auth token route
    
    disp.set_handler('v3_auth_tokens',AuthTokensV3(template_file_v3))
    
    #V3 service
    disp.set_handler('v3_services',ServicesV3(template_file_v3))

    add_hooks(app)
