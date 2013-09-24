from services.compute import compute_dispatcher
from .endpoints.availability_zones import SLComputeV2AvailabilityZones
from .endpoints.extensions import SLComputeV2Extensions
from .endpoints.flavors import SLComputeV2Flavor, SLComputeV2Flavors
from .endpoints.floating_ips import SLComputeV2OSFloatingIps
from .endpoints.keypairs import SLComputeV2Keypairs, SLComputeV2Keypair
from .endpoints.limits import SLComputeV2Limits
from .endpoints.quota_sets import SLComputeV2OSQuotaSets
from .endpoints.servers import (SLComputeV2Server, SLComputeV2Servers,
                                SLComputeV2ServersDetail,
                                SLComputeV2ServerAction)
from .endpoints.security_groups import SLComputeV2OSSecurityGroups
from .endpoints.usage import SLComputeV2Usage
from .endpoints.volumes import SLComputeV2OSVolumeAttachments

# Set handlers for the routes we support

# V2 Routes
flavor = SLComputeV2Flavor()
flavors = SLComputeV2Flavors()

compute_dispatcher.set_handler('v2_availability_zone',
                               SLComputeV2AvailabilityZones())

compute_dispatcher.set_handler('v2_extensions', SLComputeV2Extensions())

compute_dispatcher.set_handler('v2_flavor', flavor)
compute_dispatcher.set_handler('v2_flavors', flavors)
compute_dispatcher.set_handler('v2_flavors_detail', flavors)

compute_dispatcher.set_handler('v2_limits', SLComputeV2Limits())

compute_dispatcher.set_handler('v2_os_floating_ips',
                               SLComputeV2OSFloatingIps())

compute_dispatcher.set_handler('v2_os_keypair', SLComputeV2Keypair())
compute_dispatcher.set_handler('v2_os_keypairs', SLComputeV2Keypairs())

compute_dispatcher.set_handler('v2_os_quota_sets', SLComputeV2OSQuotaSets())
compute_dispatcher.set_handler('v2_os_tenant_quota_sets',
                               SLComputeV2OSQuotaSets())

compute_dispatcher.set_handler('v2_os_server_security_groups',
                               SLComputeV2OSSecurityGroups())
compute_dispatcher.set_handler('v2_os_security_groups',
                               SLComputeV2OSSecurityGroups())

compute_dispatcher.set_handler('v2_os_volume_attachments',
                               SLComputeV2OSVolumeAttachments())

compute_dispatcher.set_handler('v2_server', SLComputeV2Server())
compute_dispatcher.set_handler('v2_servers', SLComputeV2Servers())
compute_dispatcher.set_handler('v2_servers_detail', SLComputeV2ServersDetail())
compute_dispatcher.set_handler('v2_server_action', SLComputeV2ServerAction())

compute_dispatcher.set_handler('v2_tenant_flavor', flavor)
compute_dispatcher.set_handler('v2_tenant_flavors', flavors)
compute_dispatcher.set_handler('v2_tenant_flavors_detail', flavors)

compute_dispatcher.set_handler('v2_tenant_usage', SLComputeV2Usage())

# Don't forget to import the routes or else nothing will happen.
compute_dispatcher.import_routes()

#print(compute_dispatcher.get_unused_endpoints())
