from jumpgate.common.error_handling import bad_request
from operator import itemgetter
from ipaddress import ip_network

SUBNET_MASK = \
    'id, cidr, netmask, networkVlanId, networkIdentifier, gateway, version'


class SubnetV2(object):
    def on_get(self, req, resp, subnet_id):
        """
        Shows information for a specified subnet. (subnet-show)
        @param req: Http Request body
        @param resp: Http Response body
        @param subnet_id: subnet id
        @return: Bad request if the id is not a valid integer
        """
        client = req.env['sl_client']
        tenant_id = req.env['auth']['tenant_id']
        try:
            subnet_id = int(subnet_id)
        except Exception:
            return bad_request(resp, message="Malformed request body")
        subnet = client['Network_Subnet'].getObject(id=subnet_id,
                                                    mask=SUBNET_MASK)
        resp.body = {'subnet': format_subnetwork(subnet, tenant_id)}
        resp.status = 200


class SubnetsV2(object):
    """
    class SubnetsV2 returns the subnets owned by the tenant submitting the
    request, unless the request is submitted by a user with administrative
    rights.
    """

    def on_get(self, req, resp):
        """
        Handles subnet-list/subnet-show.
        @param req: Http Request body
        @param resp: Http Response body
        """
        client = req.env['sl_client']
        tenant_id = req.env['auth']['tenant_id']
        if req.get_param('name'):
            # Neutron is not using the proper endpoint to do subnet-show.
            # It is handled here as a work around.
            _filter = {
            'subnets': {'id': {'operation': int(req.get_param('name'))}}}
            subnet_matched = client['Account'].getSubnets(filter=_filter)
            if subnet_matched:
                resp.body = {
                    'subnets': [{'id': str(subnet_matched[0]['id'])}]
                }
            else:
                resp.body = {'subnets': []}

        else:
            subnets = client['Account'].getSubnets(mask=SUBNET_MASK)
            resp.body = {
                'subnets': [format_subnetwork(subnet, tenant_id) for subnet in
                            sorted(subnets, key=itemgetter('id'))]
            }
        resp.status = 200


def format_subnetwork(subnet, tenant_id):
    allocation_pools = []

    cidr = str(subnet['networkIdentifier']) + '/' + str(subnet['cidr'])

    if subnet['version'] == 4:
        # ip4 support
        allocation_pools.append({"start": str(ip_network(cidr)[0] + 2),
                                 "end": str(ip_network(cidr)[-1] - 1)})
    return {
        "name": '',
        "tenant_id": tenant_id,
        "allocation_pools": allocation_pools,
        "gateway_ip": subnet.get('gateway'),
        "ip_version": subnet.get('version'),
        "cidr": cidr,
        "id": subnet.get('id'),
        "enable_dhcp": False,
        "network_id": subnet.get('networkVlanId'),
        "dns_nameservers": [],
        "host_routes": [],
    }
