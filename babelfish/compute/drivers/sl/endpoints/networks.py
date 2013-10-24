

class OSNetworksV2(object):
    def on_get(self, req, resp, tenant_id):
        networks = []
        client = req.env['sl_client']
        sl_networks = client['Account'].getSubnets(
            mask='id, modifyDate, gateway, networkVlanId, broadcastAddress, '
            'netmask, networkIdentifier, cidr, reverseDomain, note')
        networks = [format_network(network) for network in sl_networks]
        resp.body = {'networks': networks}


class OSNetworkV2(object):
    def on_get(self, req, resp, tenant_id, network_id):
        client = req.env['sl_client']
        sl_network = client['Network_Subnet'].getObject(
            id=network_id,
            mask='id, modifyDate, gateway, networkVlanId, broadcastAddress, '
            'netmask, networkIdentifier, cidr, reverseDomain, note')
        network = format_network(sl_network)
        resp.body = {'network': network}


def format_network(sl_network):
    return {
        'label': sl_network.get('note'),
        'updated_at': sl_network['modifyDate'],
        'id': sl_network['id'],
        'gateway': sl_network.get('gateway'),
        'deleted': False,
        'vlan': sl_network['networkVlanId'],
        'broadcast': sl_network.get('broadcastAddress'),
        'netmask': sl_network['netmask'],
        'cidr': '%s/%s' % (sl_network['networkIdentifier'],
                           sl_network['cidr']),
        'dns1': sl_network.get('reverseDomain'),
    }
