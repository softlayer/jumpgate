import json


class SLComputeV2InstanceActions(object):
    def on_get(self, req, resp, tenant_id, server_id):
        client = req.env['sl_client']

        actions = []
        server = client['Virtual_Guest'].getObject(
            id=server_id,
            mask='id, accountId, '
            'activeTransaction[transactionGroup, transactionStatus],'
            'lastTransaction[transactionGroup, transactionStatus]')
        if server.get('lastTransaction'):
            actions.append(format_action(tenant_id, server['lastTransaction']))

        if server.get('activeTransaction'):
            actions.append(
                format_action(tenant_id, server['activeTransaction']))

        return json.dumps({'instanceActions': actions})


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
