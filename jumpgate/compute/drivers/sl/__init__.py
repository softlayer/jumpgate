from jumpgate.compute import compute_dispatcher
from .endpoints.availability_zones import AvailabilityZonesV2
from .endpoints.extensions import ExtensionsV2
from .endpoints.extra_specs import ExtraSpecsFlavorV2
from .endpoints.dns import DNSDomainsV2, DNSDomainEntryV2
from .endpoints.flavors import (
    FlavorV2, FlavorsV2, FlavorsDetailV2)
from .endpoints.floating_ips import OSFloatingIpsV2
from .endpoints.keypairs import KeypairsV2, KeypairV2
from .endpoints.limits import LimitsV2
from .endpoints.quota_sets import OSQuotaSetsV2
from .endpoints.servers import (ServerV2, ServersV2,
                                ServersDetailV2,
                                ServerActionV2)
from .endpoints.security_groups import OSSecurityGroupsV2
from .endpoints.usage import UsageV2
from .endpoints.volumes import OSVolumeAttachmentsV2
from .endpoints.networks import OSNetworksV2, OSNetworkV2
from .endpoints.instance_actions import InstanceActionsV2

# Set handlers for the routes we support

# V2 Routes
flavor = FlavorV2()
flavors = FlavorsV2()
flavors_detail = FlavorsDetailV2()

compute_dispatcher.set_handler('v2_availability_zone',
                               AvailabilityZonesV2())
compute_dispatcher.set_handler('v2_availability_zone_detail',
                               AvailabilityZonesV2())

compute_dispatcher.set_handler('v2_extensions', ExtensionsV2())

compute_dispatcher.set_handler('v2_os_extra_specs_flavor',
                               ExtraSpecsFlavorV2())

compute_dispatcher.set_handler('v2_flavor', flavor)
compute_dispatcher.set_handler('v2_flavors', flavors)
compute_dispatcher.set_handler('v2_flavors_detail', flavors_detail)

compute_dispatcher.set_handler('v2_os_floating_ip_dns',
                               DNSDomainsV2())
compute_dispatcher.set_handler('v2_os_floating_ip_dns_domain_entry',
                               DNSDomainEntryV2())

compute_dispatcher.set_handler('v2_limits', LimitsV2())

compute_dispatcher.set_handler('v2_os_floating_ips',
                               OSFloatingIpsV2())

compute_dispatcher.set_handler('v2_os_tenant_networks',
                               OSNetworksV2())
compute_dispatcher.set_handler('v2_os_tenant_network',
                               OSNetworkV2())
compute_dispatcher.set_handler('v2_os_networks',
                               OSNetworksV2())
compute_dispatcher.set_handler('v2_os_network',
                               OSNetworkV2())

compute_dispatcher.set_handler('v2_os_keypair', KeypairV2())
compute_dispatcher.set_handler('v2_os_keypairs', KeypairsV2())

compute_dispatcher.set_handler('v2_os_quota_sets', OSQuotaSetsV2())
compute_dispatcher.set_handler('v2_os_tenant_quota_sets',
                               OSQuotaSetsV2())

compute_dispatcher.set_handler('v2_os_server_security_groups',
                               OSSecurityGroupsV2())
compute_dispatcher.set_handler('v2_os_security_groups',
                               OSSecurityGroupsV2())

compute_dispatcher.set_handler('v2_os_volume_attachments',
                               OSVolumeAttachmentsV2())

compute_dispatcher.set_handler('v2_server', ServerV2())
compute_dispatcher.set_handler('v2_servers', ServersV2())
compute_dispatcher.set_handler('v2_servers_detail', ServersDetailV2())
compute_dispatcher.set_handler('v2_server_action', ServerActionV2())
compute_dispatcher.set_handler('v2_os_instance_actions',
                               InstanceActionsV2())

compute_dispatcher.set_handler('v2_tenant_flavor', flavor)
compute_dispatcher.set_handler('v2_tenant_flavors', flavors)
compute_dispatcher.set_handler('v2_tenant_flavors_detail', flavors_detail)

compute_dispatcher.set_handler('v2_tenant_usage', UsageV2())


# Don't forget to import the routes or else nothing will happen.
compute_dispatcher.import_routes()

#print(compute_dispatcher.get_unused_endpoints())
