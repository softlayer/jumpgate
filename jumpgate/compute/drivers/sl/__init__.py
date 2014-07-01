from jumpgate.common import sl as sl_common
from jumpgate.compute.drivers.sl import availability_zones
from jumpgate.compute.drivers.sl import dns
from jumpgate.compute.drivers.sl import extensions
from jumpgate.compute.drivers.sl import extra_specs
from jumpgate.compute.drivers.sl import flavors
from jumpgate.compute.drivers.sl import floating_ips
from jumpgate.compute.drivers.sl import index
from jumpgate.compute.drivers.sl import instance_actions
from jumpgate.compute.drivers.sl import keypairs
from jumpgate.compute.drivers.sl import limits
from jumpgate.compute.drivers.sl import networks
from jumpgate.compute.drivers.sl import quota_sets
from jumpgate.compute.drivers.sl import security_groups
from jumpgate.compute.drivers.sl import server_ips
from jumpgate.compute.drivers.sl import servers
from jumpgate.compute.drivers.sl import usage
from jumpgate.compute.drivers.sl import volumes
from jumpgate.image.drivers.sl import images


def setup_routes(app, disp):
    # V3 Routes
    # None currently supported

    # V2 Routes
    disp.set_handler('index', index.IndexV2(app))
    disp.set_handler('v2_index', index.IndexV2(app))

    flavor = flavors.FlavorV2(app)
    flavor_list = flavors.FlavorsV2(app)
    flavors_detail = flavors.FlavorsDetailV2(app)

    disp.set_handler('v2_availability_zone',
                     availability_zones.AvailabilityZonesV2())
    disp.set_handler('v2_availability_zone_detail',
                     availability_zones.AvailabilityZonesV2())

    disp.set_handler('v2_extensions', extensions.ExtensionsV2())
    disp.set_handler('v2_extension', extensions.ExtensionV2())

    disp.set_handler('v2_os_extra_specs_flavor',
                     extra_specs.ExtraSpecsFlavorV2())

    disp.set_handler('v2_flavor', flavor)
    disp.set_handler('v2_flavors', flavor_list)
    disp.set_handler('v2_flavors_detail', flavors_detail)

    disp.set_handler('v2_os_floating_ip_dns', dns.DNSDomainsV2())
    disp.set_handler('v2_os_floating_ip_dns_domain_entry',
                     dns.DNSDomainEntryV2())

    disp.set_handler('v2_limits', limits.LimitsV2())

    disp.set_handler('v2_os_floating_ips', floating_ips.OSFloatingIpsV2())

    disp.set_handler('v2_os_tenant_networks', networks.OSNetworksV2())
    disp.set_handler('v2_os_tenant_network', networks.OSNetworkV2())
    disp.set_handler('v2_os_networks', networks.OSNetworksV2())
    disp.set_handler('v2_os_network', networks.OSNetworkV2())

    disp.set_handler('v2_os_keypair', keypairs.KeypairV2())
    disp.set_handler('v2_os_keypairs', keypairs.KeypairsV2())

    disp.set_handler('v2_os_quota_sets', quota_sets.OSQuotaSetsV2())
    disp.set_handler('v2_os_tenant_quota_sets', quota_sets.OSQuotaSetsV2())

    disp.set_handler('v2_os_server_security_groups',
                     security_groups.OSSecurityGroupsV2())
    disp.set_handler('v2_os_security_groups',
                     security_groups.OSSecurityGroupsV2())

    disp.set_handler('v2_os_volume_attachments',
                     volumes.OSVolumeAttachmentsV2())
    disp.set_handler('v2_os_volume_attachments_detail',
                     volumes.OSVolumeAttachmentV2())

    disp.set_handler('v2_server', servers.ServerV2(app))
    disp.set_handler('v2_servers', servers.ServersV2(app))
    disp.set_handler('v2_servers_detail', servers.ServersDetailV2(app))
    disp.set_handler('v2_server_action', servers.ServerActionV2(app))
    disp.set_handler('v2_os_instance_actions',
                     instance_actions.InstanceActionsV2())
    disp.set_handler('v2_os_instance_action',
                     instance_actions.InstanceActionV2())

    disp.set_handler('v2_server_ips', server_ips.ServerIpsV2())
    disp.set_handler('v2_server_ips_network', server_ips.ServerIpsNetworkV2())

    disp.set_handler('v2_tenant_flavor', flavor)
    disp.set_handler('v2_tenant_flavors', flavor_list)
    disp.set_handler('v2_tenant_flavors_detail', flavors_detail)

    disp.set_handler('v2_tenant_usage', usage.UsageV2())

    disp.set_handler('v2_image', images.ImageV1(app))
    disp.set_handler('v2_images', images.ImagesV2(app))
    disp.set_handler('v2_images_detail', images.ImagesV2(app))

    sl_common.add_hooks(app)
