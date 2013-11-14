from jumpgate.common.dispatcher import Dispatcher
from jumpgate.api import app

identity_dispatcher = Dispatcher(app)

# V3 API - http://api.openstack.org/api-ref-identity.html#identity-v3

# Tokens
identity_dispatcher.add_endpoint('v3_tokens', '/v3/tokens')

# Service Catalog
identity_dispatcher.add_endpoint('v3_services', '/v3/services')
identity_dispatcher.add_endpoint('v3_services_with_id',
                                 '/v3/services/{service_id}')
# Endpoints
identity_dispatcher.add_endpoint('v3_endpoints', '/v3/endpoints')
identity_dispatcher.add_endpoint('v3_endpoints_with_id',
                                 '/v3/endpoints/{endpoint_id}')

# Domains
identity_dispatcher.add_endpoint('v3_domains', '/v3/domains')
identity_dispatcher.add_endpoint('v3_domains_with_id',
                                 '/v3/domains/{domain_id}')
identity_dispatcher.add_endpoint('v3_domain_user_roles',
                                 '/v3/domains/{domain_id}/users/{user_id}'
                                 '/roles')
identity_dispatcher.add_endpoint('v3_domain_user_role',
                                 '/v3/domains/{domain_id}/users/{user_id}'
                                 '/role/{role_id}')
identity_dispatcher.add_endpoint('v3_domain_group_roles',
                                 '/v3/domains/{domain_id}/groups/{group_id}'
                                 '/roles')
identity_dispatcher.add_endpoint('v3_domain_group_role',
                                 '/v3/domains/{domain_id}/groups/{group_id}'
                                 '/role/{role_id}')

# Projects
identity_dispatcher.add_endpoint('v3_projects', '/v3/projects')
identity_dispatcher.add_endpoint('v3_projects_with_id',
                                 '/v3/projects/{project_id}')
identity_dispatcher.add_endpoint('v3_project_users',
                                 '/v3/projects/{project_id}/users')
identity_dispatcher.add_endpoint('v3_project_user_roles',
                                 '/v3/projects/{project_id}/users/{user_id}'
                                 '/roles')
identity_dispatcher.add_endpoint('v3_project_user_role',
                                 '/v3/projects/{project_id}/users/{user_id}'
                                 '/roles/{role_id}')
identity_dispatcher.add_endpoint('v3_project_group_roles',
                                 '/v3/projects/{project_id}/groups/{group_id}'
                                 '/roles')
identity_dispatcher.add_endpoint('v3_project_role',
                                 '/v3/projects/{project_id}/{role_id}')

# Users
identity_dispatcher.add_endpoint('v3_users', '/v3/users')
identity_dispatcher.add_endpoint('v3_user', '/v3/users/{user_id}')
identity_dispatcher.add_endpoint('v3_user_groups',
                                 '/v3/users/{user_id}/groups')
identity_dispatcher.add_endpoint('v3_user_projects',
                                 '/v3/users/{user_id}/projects')
identity_dispatcher.add_endpoint('v3_user_roles', '/v3/users/{user_id}/roles')

# Groups
identity_dispatcher.add_endpoint('v3_groups', '/v3/groups')
identity_dispatcher.add_endpoint('v3_group', '/v3/groups/{group_id}')
identity_dispatcher.add_endpoint('v3_group_users',
                                 '/v3/groups/{group_id}/users')
identity_dispatcher.add_endpoint('v3_group_user',
                                 '/v3/groups/{group_id}/users/{user_id}')

# Credentials
identity_dispatcher.add_endpoint('v3_credentails', '/v3/credentials')
identity_dispatcher.add_endpoint('v3_credentail',
                                 '/v3/credentials/{credential_id}')

# Roles
identity_dispatcher.add_endpoint('v3_roles', '/v3/roles')
identity_dispatcher.add_endpoint('v3_role', '/v3/roles/{role_id}')
identity_dispatcher.add_endpoint('v3_role_users', '/v3/roles/{role_id}/users')

# Policies
identity_dispatcher.add_endpoint('v3_policies', '/v3/policies')
identity_dispatcher.add_endpoint('v3_policy', '/v3/policies/{policy_id}')

# V2.0 - http://api.openstack.org/api-ref-identity.html#identity

# NOTE - These endpoint are used by both the regular 2.0 and the admin 2.0 APIs
# at the same time!
identity_dispatcher.add_endpoint('v2_auth_index', '/v2.0')
identity_dispatcher.add_endpoint('v2_extensions', '/v2.0/extensions')
identity_dispatcher.add_endpoint('v2_extension_alias',
                                 '/v2.0/extensions/{alias}')
identity_dispatcher.add_endpoint('v2_tokens', '/v2.0/tokens')
identity_dispatcher.add_endpoint('v2_token_tenants', '/v2.0/tokens/tenants')

# V2.0 Admin API - http://api.openstack.org/api-ref-identity.html#identity-admin-v2.0
# This list only includes those not defined above.

identity_dispatcher.add_endpoint('v2_token', '/v2.0/tokens/{token_id}')
identity_dispatcher.add_endpoint('v2_token_endpoints',
                                 '/v2.0/tokens/{token_id}/endpoints')
identity_dispatcher.add_endpoint('v2_users', '/v2.0/users')
identity_dispatcher.add_endpoint('v2_user', '/v2.0/users/{user_id}')
identity_dispatcher.add_endpoint('v2_user_roles',
                                 '/v2.0/users/{user_id}/roles')
identity_dispatcher.add_endpoint('v2_tenants', '/v2.0/tenants')
identity_dispatcher.add_endpoint('v2_tenant', '/v2.0/tenants/{tenant_id}')
identity_dispatcher.add_endpoint('v2_tenant_user_roles',
                                 '/v2.0/tenants/{tenant_id}/users/{user_id}'
                                 '/roles')
