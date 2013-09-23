from services.common.dispatcher import Dispatcher
from core import api

compute_dispatcher = Dispatcher(api)

# V2 API - http://api.openstack.org/api-ref.html#compute

# Extensions
compute_dispatcher.add_endpoint('v2_extensions', '/v2/{tenant_id}/extensions')
compute_dispatcher.add_endpoint('v2_extension',
                                '/v2/{tenant_id}/extensions/{alias}')

# Limits
compute_dispatcher.add_endpoint('v2_limits', '/v2/{tenant_id}/limits')

# Servers
compute_dispatcher.add_endpoint('v2_servers', '/v2/{tenant_id}/servers')
compute_dispatcher.add_endpoint('v2_servers_detail',
                                '/v2/{tenant_id}/servers/detail')
compute_dispatcher.add_endpoint('v2_server',
                                '/v2/{tenant_id}/servers/{server_id}')

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
                                '/v2/{tenant_id}/servers/action')

# Flavors
compute_dispatcher.add_endpoint('v2_flavors', '/v2/flavors')
compute_dispatcher.add_endpoint('v2_flavors_detail', '/v2/flavors/detail')
compute_dispatcher.add_endpoint('v2_flavor', '/v2/flavors/{flavor_id}')
compute_dispatcher.add_endpoint('v2_tenant_flavors', '/v2/{tenant_id}/flavors')
compute_dispatcher.add_endpoint('v2_tenant_flavors_detail',
                                '/v2/{tenant_id}/flavors/detail')
compute_dispatcher.add_endpoint('v2_tenant_flavor',
                                '/v2/{tenant_id}/flavors/{flavor_id}')

# Extensions - Not all drivers will support all of these

# Security Groups
compute_dispatcher.add_endpoint('v2_os_security_groups',
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
