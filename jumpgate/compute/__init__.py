

def add_endpoints(disp):
    # V2 API - http://api.openstack.org/api-ref-compute.html#compute

    disp.add_endpoint('index', '/')

    disp.add_endpoint('v3_index', '/v3')
    disp.add_endpoint('v2_index', '/v2')

    # Extensions
    disp.add_endpoint('v2_extensions', '/v2/{tenant_id}/extensions')
    disp.add_endpoint('v2_extension', '/v2/{tenant_id}/extensions/{alias}')

    # Limits
    disp.add_endpoint('v2_limits', '/v2/{tenant_id}/limits')

    # Servers
    disp.add_endpoint('v2_server', '/v2/{tenant_id}/servers/{server_id}')
    disp.add_endpoint('v2_servers', '/v2/{tenant_id}/servers')
    disp.add_endpoint('v2_servers_detail', '/v2/{tenant_id}/servers/detail')

    # Server Metadata
    disp.add_endpoint('v2_server_metadata',
                      '/v2/{tenant_id}/servers/{server_id}/metadata')
    disp.add_endpoint('v2_server_metadata_key',
                      '/v2/{tenant_id}/servers/{server_id}/metadata/{key}')

    # Server Addresses
    disp.add_endpoint('v2_server_ips',
                      '/v2/{tenant_id}/servers/{server_id}/ips')
    disp.add_endpoint(
        'v2_server_ips_network',
        '/v2/{tenant_id}/servers/{server_id}/ips/{network_label}')

    # Server Actions
    disp.add_endpoint('v2_server_action',
                      '/v2/{tenant_id}/servers/{instance_id}/action')
    disp.add_endpoint(
        'v2_os_instance_actions',
        '/v2/{tenant_id}/servers/{server_id}/os-instance-actions')
    disp.add_endpoint(
        'v2_os_instance_action',
        '/v2/{tenant_id}/servers/{server_id}/os-instance-actions/{action_id}')

    # Images
    disp.add_endpoint('v2_image', '/v2/{tenant_id}/images/{image_guid}')
    disp.add_endpoint('v2_images', '/v2/{tenant_id}/images')
    disp.add_endpoint('v2_images_detail', '/v2/{tenant_id}/images/detail')

    # Flavors
    disp.add_endpoint('v2_flavor', '/v2/flavors/{flavor_id}')
    disp.add_endpoint('v2_flavors', '/v2/flavors')
    disp.add_endpoint('v2_flavors_detail', '/v2/flavors/detail')
    disp.add_endpoint('v2_tenant_flavor',
                      '/v2/{tenant_id}/flavors/{flavor_id}')
    disp.add_endpoint('v2_tenant_flavors', '/v2/{tenant_id}/flavors')
    disp.add_endpoint('v2_tenant_flavors_detail',
                      '/v2/{tenant_id}/flavors/detail')

    # Extensions - http://api.openstack.org/api-ref-compute.html#compute-ext
    # Note: Not all drivers will support all of these

    # Extended Availability Zones
    disp.add_endpoint('v2_availability_zone',
                      '/v2/{tenant_id}/os-availability-zone')
    disp.add_endpoint('v2_availability_zone_detail',
                      '/v2/{tenant_id}/os-availability-zone/detail')

    # Flavor Extra Specs
    disp.add_endpoint('v2_os_extra_specs_flavor',
                      '/v2/{tenant_id}/flavors/{flavor_id}/os-extra_specs')
    disp.add_endpoint(
        'v2_os_extra_specs_flavor_key',
        '/v2/{tenant_id}/flavors/{flavor_id}/os-extra_specs/{key_id}')

    # Floating IPs
    disp.add_endpoint('v2_os_floating_ips', '/v2/{tenant_id}/os-floating-ips')
    disp.add_endpoint('v2_os_floating_ips_id',
                      '/v2/{tenant_id}/os-floating-ips/{id}')

    # Floating IP DNS
    disp.add_endpoint('v2_os_floating_ip_dns',
                      '/v2/{tenant_id}/os-floating-ip-dns')
    disp.add_endpoint('v2_os_floating_ip_dns_domain',
                      '/v2/{tenant_id}/os-floating-ip-dns/{domain}')
    disp.add_endpoint(
        'v2_os_floating_ip_dns_domain_entry',
        '/v2/{tenant_id}/os-floating-ip-dns/{domain}/entries/{entry}')

    # Floating IP Pools
    disp.add_endpoint('v2_os_floating_ip_pools',
                      '/v2/{tenant_id}/os-floating-ip-pools')

    # Host Aggregates
    disp.add_endpoint('v2_os_aggregates',
                      '/v2/{tenant_id}/os-aggregates')
    disp.add_endpoint('v2_os_aggregate',
                      '/v2/{tenant_id}/os-aggregates/{aggregate_id}')
    disp.add_endpoint('v2_os_aggregate_action',
                      '/v2/{tenant_id}/os-aggregates/{aggregate_id}/action')

    # Hypervisors
    disp.add_endpoint('v2_os_hypervisors', '/v2/{tenant_id}/os-hypervisors')
    disp.add_endpoint('v2_os_hypervisors_detail',
                      '/v2/{tenant_id}/os-hypervisors/detail')
    disp.add_endpoint('v2_os_hypervisors_statistics',
                      '/v2/{tenant_id}/os-hypervisors/statistics')

    # Keypairs
    disp.add_endpoint('v2_os_keypairs', '/v2/{tenant_id}/os-keypairs')
    disp.add_endpoint('v2_os_keypair',
                      '/v2/{tenant_id}/os-keypairs/{keypair_name}')

    # Manage Services
    disp.add_endpoint('v2_os_services', '/v2/{tenant_id}/os-services')
    disp.add_endpoint('v2_os_services_enable',
                      '/v2/{tenant_id}/os-services/enable')
    disp.add_endpoint('v2_os_services_disable',
                      '/v2/{tenant_id}/os-services/disable')

    # Networks
    disp.add_endpoint('v2_os_tenant_networks',
                      '/v2/{tenant_id}/os-tenant-networks')
    disp.add_endpoint('v2_os_tenant_network',
                      '/v2/{tenant_id}/os-tenant-networks/{network_id}')
    disp.add_endpoint('v2_os_networks', '/v2/{tenant_id}/os-networks')
    disp.add_endpoint('v2_os_network',
                      '/v2/{tenant_id}/os-networks/{network_id}')

    # Quota Sets
    disp.add_endpoint('v2_os_quota_sets', '/v2/{tenant_id}/os-quota-sets')
    disp.add_endpoint('v2_os_quota_sets_default',
                      '/v2/{tenant_id}/os-quota-sets/default')
    disp.add_endpoint('v2_os_quota_sets_target',
                      '/v2/{tenant_id}/os-quota-sets/{target_id}')
    disp.add_endpoint('v2_os_quota_sets_target_defaults',
                      '/v2/{tenant_id}/os-quota-sets/{target_id}/defaults')
    disp.add_endpoint('v2_os_quota_sets_user',
                      '/v2/{tenant_id}/os-quota-sets/user={user_id}')
    disp.add_endpoint('v2_os_tenant_quota_sets',
                      '/v2/{tenant_id}/os-quota-sets/{account_id}')
    disp.add_endpoint('v1_os_quota_sets_target',
                      '/v1/{tenant_id}/os-quota-sets/{target_id}')
    disp.add_endpoint('v1_os_quota_sets_target_defaults',
                      '/v1/{tenant_id}/os-quota-sets/{target_id}/defaults')

    # Security Groups
    disp.add_endpoint('v2_os_security_groups',
                      '/v2/{tenant_id}/os-security-groups')
    disp.add_endpoint(
        'v2_os_server_security_groups',
        '/v2/{tenant_id}/servers/{instance_id}/os-security-groups')

    # Usage Reports
    disp.add_endpoint('v2_tenants_usage',
                      '/v2/{tenant_id}/os-simple-tenant-usage')
    disp.add_endpoint('v2_tenant_usage',
                      '/v2/{tenant_id}/os-simple-tenant-usage/{target_id}')

    # Volume Attachments
    disp.add_endpoint(
        'v2_os_volume_attachments_detail',
        '/v2/{tenant_id}/servers/{instance_id}/os-volume_attachments/'
        '{volume_id}')
    disp.add_endpoint(
        'v2_os_volume_attachments',
        '/v2/{tenant_id}/servers/{instance_id}/os-volume_attachments')
