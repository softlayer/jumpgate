import operator

import ipaddress

from jumpgate.common import error_handling

SUBNET_MASK = ('id, cidr, netmask, networkVlanId, networkIdentifier, gateway, '
               'version')


class SubnetV2(object):
    def on_get(self, req, resp, subnet_id):
        """Shows information for a specified subnet. (subnet-show)

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
            return error_handling.bad_request(resp,
                                              message="Malformed request body")

        subnet = client['Network_Subnet'].getObject(id=subnet_id,
                                                    mask=SUBNET_MASK)
        resp.body = {'subnet': format_subnetwork(subnet, tenant_id)}
        resp.status = 200


class SubnetsV2(object):
    """class SubnetsV2 returns the available subnets."""

    def on_get(self, req, resp):
        """Handles subnet-list/subnet-show.

        @param req: Http Request body
        @param resp: Http Response body
        """
        client = req.env['sl_client']
        tenant_id = req.env['auth']['tenant_id']

        _filter = {'subnets': {}}
        if req.get_param('name'):
            _filter['subnets']['id'] = {
                'operation': req.get_param('name')}

        subnets = client['Account'].getSubnets(mask=SUBNET_MASK,
                                               filter=_filter)
        resp.body = {
            'subnets': [format_subnetwork(subnet, tenant_id)
                        for subnet in sorted(subnets,
                                             key=operator.itemgetter('id'))]
        }
        resp.status = 200


def format_subnetwork(subnet, tenant_id):
    allocation_pools = []

    cidr = str(subnet['networkIdentifier']) + '/' + str(subnet['cidr'])

    allocation_pools.append({"start": str(ipaddress.ip_network(cidr)[0] + 2),
                             "end": str(ipaddress.ip_network(cidr)[-1] - 1)})
    return {
        "name": '',
        "tenant_id": tenant_id,
        "allocation_pools": allocation_pools,
        "gateway_ip": subnet.get('gateway'),
        "ip_version": subnet.get('version'),
        "cidr": cidr,
        "id": str(subnet.get('id')),
        "enable_dhcp": False,
        "network_id": subnet.get('networkVlanId'),
        "dns_nameservers": [],
        "host_routes": [],
    }
