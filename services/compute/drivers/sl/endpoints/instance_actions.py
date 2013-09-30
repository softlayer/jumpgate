import json

from SoftLayer import SoftLayerAPIError
from services.common.error_handling import not_found


class SLComputeV2InstanceActions(object):
    def on_get(self, req, resp, tenant_id, server_id):
        try:
            int(server_id)
        except ValueError:
            return not_found(resp, 'Instance could not be found')

        client = req.env['sl_client']

        actions = []
        try:
            server = client['Virtual_Guest'].getObject(
                id=server_id,
                mask='id, accountId, '
                'activeTransaction[transactionGroup, transactionStatus],'
                'lastTransaction[transactionGroup, transactionStatus]')
        except SoftLayerAPIError as e:
            if e.faultCode == 'SoftLayer_Exception_ObjectNotFound':
                return not_found(resp, 'Instance could not be found')
            raise

        if server.get('lastTransaction'):
            actions.append(format_action(tenant_id, server['lastTransaction']))

        if server.get('activeTransaction'):
            actions.append(
                format_action(tenant_id, server['activeTransaction']))

        resp.body = json.dumps({'instanceActions': actions})


def format_action(account_id, transaction):
    sl_group = transaction['transactionGroup']['name'].lower()
    action = sl_group
    if 'reload' in sl_group:
        action = 'rebuild'
    elif 'provision' in sl_group:
        action = 'create'
    elif 'reclaim' in sl_group:
        action = 'remove'

    return {
        'action': action,
        'instance_uuid': transaction['guestId'],
        'message': '',
        'project_id': account_id,
        'request_id': transaction['id'],
        'start_time': transaction['createDate'],
    }
