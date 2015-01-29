import SoftLayer

from jumpgate.common import error_handling


class ServerIpsV2(object):
    def on_get(self, req, resp, tenant_id, server_id):
        client = req.env['sl_client']
        cci = SoftLayer.VSManager(client)

        instance = cci.get_instance(
            server_id, mask='id, primaryIpAddress, primaryBackendIpAddress')

        addresses = {}
        if instance.get('primaryIpAddress'):
            addresses['public'] = [{
                'version': 4,
                'addr': instance['primaryIpAddress'],
            }]

        if instance.get('primaryBackendIpAddress'):
            addresses['private'] = [{
                'version': 4,
                'addr': instance['primaryBackendIpAddress'],
            }]

        resp.body = {'addresses': addresses}


class ServerIpsNetworkV2(object):
    def on_get(self, req, resp, tenant_id, server_id, network_label):
        network_label = network_label.lower()

        network_mask = None
        if network_label == 'public':
            network_mask = 'primaryIpAddress'
        elif network_label == 'private':
            network_mask = 'primaryBackendIpAddress'
        else:
            return error_handling.not_found(resp,
                                            message='Network does not exist')

        client = req.env['sl_client']
        cci = SoftLayer.VSManager(client)
        instance = cci.get_instance(server_id, mask='id, ' + network_mask)

        resp.body = {
            network_label: [
                {'version': 4, 'addr': instance[network_mask]},
            ]
        }
