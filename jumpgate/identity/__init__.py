

def add_endpoints(disp):
    # Versions
    disp.add_endpoint('versions', '/')

    # V3 API - http://api.openstack.org/api-ref-identity.html#identity-v3

    disp.add_endpoint('v3_auth_index', '/v3')
    # Tokens
    
    disp.add_endpoint('v3_auth_tokens', '/v3/auth/tokens')
    
    

    # Service Catalog
    disp.add_endpoint('v3_services', '/v3/services')
    disp.add_endpoint('v3_services_with_id', '/v3/services/{service_id}')
    # Endpoints
    disp.add_endpoint('v3_endpoints', '/v3/endpoints')
    disp.add_endpoint('v3_endpoints_with_id',
                      '/v3/endpoints/{endpoint_id}')

    # Domains
    disp.add_endpoint('v3_domains', '/v3/domains')
    disp.add_endpoint('v3_domains_with_id',
                      '/v3/domains/{domain_id}')
    disp.add_endpoint('v3_domain_user_roles',
                      '/v3/domains/{domain_id}/users/{user_id}'
                      '/roles')
    disp.add_endpoint('v3_domain_user_role',
                      '/v3/domains/{domain_id}/users/{user_id}'
                      '/role/{role_id}')
    disp.add_endpoint('v3_domain_group_roles',
                      '/v3/domains/{domain_id}/groups/{group_id}'
                      '/roles')
    disp.add_endpoint('v3_domain_group_role',
                      '/v3/domains/{domain_id}/groups/{group_id}'
                      '/role/{role_id}')

    # Projects
    disp.add_endpoint('v3_projects', '/v3/projects')
    disp.add_endpoint('v3_projects_with_id',
                      '/v3/projects/{project_id}')
    disp.add_endpoint('v3_project_users',
                      '/v3/projects/{project_id}/users')
    disp.add_endpoint('v3_project_user_roles',
                      '/v3/projects/{project_id}/users/{user_id}'
                      '/roles')
    disp.add_endpoint('v3_project_user_role',
                      '/v3/projects/{project_id}/users/{user_id}'
                      '/roles/{role_id}')
    disp.add_endpoint('v3_project_group_roles',
                      '/v3/projects/{project_id}/groups/{group_id}'
                      '/roles')
    disp.add_endpoint('v3_project_role',
                      '/v3/projects/{project_id}/{role_id}')

    # Users
    disp.add_endpoint('v3_users', '/v3/users')
    disp.add_endpoint('v3_user', '/v3/users/{user_id}')
    disp.add_endpoint('v3_user_groups',
                      '/v3/users/{user_id}/groups')
    disp.add_endpoint('v3_user_projects',
                      '/v3/users/{user_id}/projects')
    disp.add_endpoint('v3_user_roles', '/v3/users/{user_id}/roles')

    # Groups
    disp.add_endpoint('v3_groups', '/v3/groups')
    disp.add_endpoint('v3_group', '/v3/groups/{group_id}')
    disp.add_endpoint('v3_group_users',
                      '/v3/groups/{group_id}/users')
    disp.add_endpoint('v3_group_user',
                      '/v3/groups/{group_id}/users/{user_id}')

    # Credentials
    disp.add_endpoint('v3_credentails', '/v3/credentials')
    disp.add_endpoint('v3_credentail',
                      '/v3/credentials/{credential_id}')

    # Roles
    disp.add_endpoint('v3_roles', '/v3/roles')
    disp.add_endpoint('v3_role', '/v3/roles/{role_id}')
    disp.add_endpoint('v3_role_users', '/v3/roles/{role_id}/users')

    # Policies
    disp.add_endpoint('v3_policies', '/v3/policies')
    disp.add_endpoint('v3_policy', '/v3/policies/{policy_id}')

    # V2.0 - http://api.openstack.org/api-ref-identity.html#identity

    # NOTE - These endpoint are used by both the regular 2.0 and the admin
    # 2.0 APIs at the same time!
    disp.add_endpoint('v2_auth_index', '/v2.0')
    disp.add_endpoint('v2_extensions', '/v2.0/extensions')
    disp.add_endpoint('v2_extension_alias',
                      '/v2.0/extensions/{alias}')
    disp.add_endpoint('v2_tokens', '/v2.0/tokens')
    disp.add_endpoint('v2_token_tenants', '/v2.0/tokens/tenants')

    # V2.0 Admin API
    # http://api.openstack.org/api-ref-identity.html#identity-admin-v2.0
    # This list only includes those not defined above.

    disp.add_endpoint('v2_token', '/v2.0/tokens/{token_id}')
    disp.add_endpoint('v2_token_endpoints',
                      '/v2.0/tokens/{token_id}/endpoints')
    disp.add_endpoint('v2_users', '/v2.0/users')
    disp.add_endpoint('v2_user', '/v2.0/users/{user_id}')
    disp.add_endpoint('v2_user_roles',
                      '/v2.0/users/{user_id}/roles')
    disp.add_endpoint('v2_tenants', '/v2.0/tenants')
    disp.add_endpoint('v2_tenant', '/v2.0/tenants/{tenant_id}')
    disp.add_endpoint('v2_tenant_user_roles',
                      '/v2.0/tenants/{tenant_id}/users/{user_id}/roles')
