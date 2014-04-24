

class NetworksV2(object):
    def on_get(self, req, resp):
        client = req.env['sl_client']
        vlans = client['Account'].getNetworkVlans(mask='id, name, subnets')
        resp.body = {'networks': [format_network(vlan) for vlan in vlans]}


def format_network(vlan):
    return {
        'status': 'ACTIVE',
        'subnets': [str(subnet['id']) for subnet in vlan['subnets']],
        'admin_state_up': True,
        'name': vlan.get('name'),
        'id': str(vlan['id']),
    }
