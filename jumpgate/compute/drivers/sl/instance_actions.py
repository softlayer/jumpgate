import iso8601
from SoftLayer import SoftLayerAPIError

from jumpgate.common.error_handling import not_found


class InstanceActionsV2(object):
    def on_get(self, req, resp, tenant_id, server_id):
        client = req.env['sl_client']

        try:
            server = client['Virtual_Guest'].getObject(
                id=server_id, mask='id, accountId, createDate')
        except SoftLayerAPIError as e:
            if e.faultCode == 'SoftLayer_Exception_ObjectNotFound':
                return not_found(resp, 'Instance could not be found')
            raise

        actions = client['Event_Log'].getAllObjects(filter={
            'userType': {'operation': 'SYSTEM'},
            'objectName': {'operation': 'CCI'},
            'objectId': {'operation': server_id}})

        resp.body = {'instanceActions': [format_action(server, action)
                                         for action in actions]}


class InstanceActionV2(object):
    def on_get(self, req, resp, tenant_id, server_id, action_id):
        client = req.env['sl_client']

        try:
            server = client['Virtual_Guest'].getObject(
                id=server_id, mask='id, accountId, createDate')
        except SoftLayerAPIError as e:
            if e.faultCode == 'SoftLayer_Exception_ObjectNotFound':
                return not_found(resp, 'Instance could not be found')
            raise

        actions = client['Event_Log'].getAllObjects(
            filter={
                'userType': {'operation': 'SYSTEM'},
                'objectName': {'operation': 'CCI'},
                'objectId': {'operation': server_id},
                'traceId': {'operation': action_id}})

        if len(actions) == 0:
            return not_found(resp, 'action could not be found')

        resp.body = {'instanceAction': format_action(server, actions[0])}


def format_action(server, event):
    event_name = event['eventName'].lower().replace(' ', '_')
    server_created = iso8601.parse_date(server['createDate'])
    event_date = iso8601.parse_date(event['eventCreateDate'])
    if event_name == 'power_on':
        if abs((event_date - server_created).total_seconds()) < 300:
            event_name = 'create'
    elif event_name == 'os_reload':
        event_name = 'rebuild'

    formatted_time = event_date.strftime("%Y-%m-%d %H:%M:%S.%f")
    return {'action': event_name,
            'instance_uuid': event['objectId'],
            'message': event['metaData'],
            'project_id': server['accountId'],
            'request_id': event['traceId'],
            'start_time': formatted_time}
