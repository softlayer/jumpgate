from babelfish.common.dispatcher import Dispatcher
from babelfish.api import app

compute_dispatcher = Dispatcher(app)

# V2 API - http://api.openstack.org/api-ref-compute.html#compute

# Extensions
compute_dispatcher.add_endpoint('v2_extensions', '/v2/{tenant_id}/extensions')
compute_dispatcher.add_endpoint('v2_extension',
                                '/v2/{tenant_id}/extensions/{alias}')

# Limits
compute_dispatcher.add_endpoint('v2_limits', '/v2/{tenant_id}/limits')

# Servers
compute_dispatcher.add_endpoint('v2_server',
                                '/v2/{tenant_id}/servers/{server_id}')
compute_dispatcher.add_endpoint('v2_servers', '/v2/{tenant_id}/servers')
compute_dispatcher.add_endpoint('v2_servers_detail',
                                '/v2/{tenant_id}/servers/detail')

# Server Metadata
compute_dispatcher.add_endpoint('v2_server_metadata',
                                '/v2/{tenant_id}/servers/{server_id}/metadata')
compute_dispatcher.add_endpoint('v2_server_metadata_key',
                                '/v2/{tenant_id}/servers/{server_id}/metadata'
                                '/{key}')

# Server Addresses
compute_dispatcher.add_endpoint('v2_server_ips',
                                '/v2/{tenant_id}/servers{server_id}/ips')
compute_dispatcher.add_endpoint('v2_server_ips_network',
                                '/v2/{tenant_id}/servers{server_id}/ips'
                                '/{network_label}')

# Server Actions
compute_dispatcher.add_endpoint('v2_server_action',
                                '/v2/{tenant_id}/servers/{instance_id}/action')
compute_dispatcher.add_endpoint(
    'v2_os_instance_actions',
    '/v2/{tenant_id}/servers/{server_id}/os-instance-actions')

# Flavors
compute_dispatcher.add_endpoint('v2_flavor', '/v2/flavors/{flavor_id}')
compute_dispatcher.add_endpoint('v2_flavors', '/v2/flavors')
compute_dispatcher.add_endpoint('v2_flavors_detail', '/v2/flavors/detail')
compute_dispatcher.add_endpoint('v2_tenant_flavor',
                                '/v2/{tenant_id}/flavors/{flavor_id}')
compute_dispatcher.add_endpoint('v2_tenant_flavors', '/v2/{tenant_id}/flavors')
compute_dispatcher.add_endpoint('v2_tenant_flavors_detail',
                                '/v2/{tenant_id}/flavors/detail')

# Extensions - http://api.openstack.org/api-ref-compute.html#compute-ext
# Note: Not all drivers will support all of these

# Extended Availability Zones
compute_dispatcher.add_endpoint('v2_availability_zone',
                                '/v2/{tenant_id}/os-availability-zone')
compute_dispatcher.add_endpoint('v2_availability_zone_detail',
                                '/v2/{tenant_id}/os-availability-zone/detail')

# Flavor Extra Specs
compute_dispatcher.add_endpoint('v2_os_extra_specs_flavor',
                                '/v2/{tenant_id}/flavors/{flavor_id}'
                                '/os-extra_specs')
compute_dispatcher.add_endpoint('v2_os_extra_specs_flavor_key',
                                '/v2/{tenant_id}/flavors/{flavor_id}'
                                '/os-extra_specs/{key_id}')

# Floating IPs
compute_dispatcher.add_endpoint('v2_os_floating_ips',
                                '/v2/{tenant_id}/os-floating-ips')
compute_dispatcher.add_endpoint('v2_os_floating_ips_id',
                                '/v2/{tenant_id}/os-floating-ips/{id}')

# Floating IP DNS
compute_dispatcher.add_endpoint('v2_os_floating_ip_dns',
                                '/v2/{tenant_id}/os-floating-ip-dns')
compute_dispatcher.add_endpoint('v2_os_floating_ip_dns_domain',
                                '/v2/{tenant_id}/os-floating-ip-dns/{domain}')
compute_dispatcher.add_endpoint('v2_os_floating_ip_dns_domain_entry',
                                '/v2/{tenant_id}/os-floating-ip-dns/{domain}'
                                '/entries/{entry}')

# Floating IP Pools
compute_dispatcher.add_endpoint('v2_os_floating_ip_pools',
                                '/v2/{tenant_id}/os-floating-ip-pools')

# Host Aggregates
compute_dispatcher.add_endpoint('v2_os_aggregates',
                                '/v2/{tenant_id}/os-aggregates')
compute_dispatcher.add_endpoint('v2_os_aggregate',
                                '/v2/{tenant_id}/os-aggregates/{aggregate_id}')
compute_dispatcher.add_endpoint('v2_os_aggregate_action',
                                '/v2/{tenant_id}/os-aggregates/{aggregate_id}'
                                '/action')

# Hypervisors
compute_dispatcher.add_endpoint('v2_os_hypervisors',
                                '/v2/{tenant_id}/os-hypervisors')
compute_dispatcher.add_endpoint('v2_os_hypervisors_detail',
                                '/v2/{tenant_id}/os-hypervisors/detail')
compute_dispatcher.add_endpoint('v2_os_hypervisors_statistics',
                                '/v2/{tenant_id}/os-hypervisors/statistics')

# Keypairs
compute_dispatcher.add_endpoint('v2_os_keypairs',
                                '/v2/{tenant_id}/os-keypairs')
compute_dispatcher.add_endpoint('v2_os_keypair',
                                '/v2/{tenant_id}/os-keypairs/{keypair_name}')

# Manage Services
compute_dispatcher.add_endpoint('v2_os_services',
                                '/v2/{tenant_id}/os-services')
compute_dispatcher.add_endpoint('v2_os_services_enable',
                                '/v2/{tenant_id}/os-services/enable')
compute_dispatcher.add_endpoint('v2_os_services_disable',
                                '/v2/{tenant_id}/os-services/disable')

# Networks
compute_dispatcher.add_endpoint('v2_os_tenant_networks',
                                '/v2/{tenant_id}/os-tenant-networks')
compute_dispatcher.add_endpoint('v2_os_tenant_network',
                                '/v2/{tenant_id}/os-tenant-networks'
                                '/{network_id}')
compute_dispatcher.add_endpoint('v2_os_networks',
                                '/v2/{tenant_id}/os-networks')
compute_dispatcher.add_endpoint('v2_os_network',
                                '/v2/{tenant_id}/os-networks/{network_id}')

# Quota Sets
compute_dispatcher.add_endpoint('v2_os_quota_sets',
                                '/v2/{tenant_id}/os-quota-sets')
compute_dispatcher.add_endpoint('v2_os_quota_sets_default',
                                '/v2/{tenant_id}/os-quota-sets/default')
compute_dispatcher.add_endpoint('v2_os_quota_sets_target',
                                '/v2/{tenant_id}/os-quota-sets/{target_id}')
compute_dispatcher.add_endpoint('v2_os_quota_sets_target_defaults',
                                '/v2/{tenant_id}/os-quota-sets/{target_id}'
                                '/defaults')
compute_dispatcher.add_endpoint('v2_os_quota_sets_user',
                                '/v2/{tenant_id}/os-quota-sets/user={user_id}')
compute_dispatcher.add_endpoint('v2_os_tenant_quota_sets',
                                '/v2/{tenant_id}/os-quota-sets/{account_id}')
compute_dispatcher.add_endpoint('v1_os_quota_sets_target',
                                '/v1/{tenant_id}/os-quota-sets/{target_id}')
compute_dispatcher.add_endpoint('v1_os_quota_sets_target_defaults',
                                '/v1/{tenant_id}/os-quota-sets/{target_id'
                                '}/defaults')

# Security Groups
compute_dispatcher.add_endpoint('v2_os_security_groups',
                                '/v2/{tenant_id}/os-security-groups')
compute_dispatcher.add_endpoint('v2_os_server_security_groups',
                                '/v2/{tenant_id}/servers/{instance_id}'
                                '/os-security-groups')

# Usage Reports
compute_dispatcher.add_endpoint('v2_tenants_usage',
                                '/v2/{tenant_id}/os-simple-tenant-usage')
compute_dispatcher.add_endpoint('v2_tenant_usage',
                                '/v2/{tenant_id}/os-simple-tenant-usage'
                                '/{target_id}')

# Volume Attachments
compute_dispatcher.add_endpoint('v2_os_volume_attachments',
                                '/v2/{tenant_id}/servers/{instance_id}'
                                '/os-volume_attachments')
