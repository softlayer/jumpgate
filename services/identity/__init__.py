from services.common.dispatcher import Dispatcher
from core import api

identity_dispatcher = Dispatcher(api)

# V3 - http://api.openstack.org/api-ref.html#identity-v3

# Versions
identity_dispatcher.add_endpoint('v3_index', '/v3')

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
