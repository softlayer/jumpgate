import json
import falcon

from services.common.nested_dict import lookup
#from slapistack.utils.error_handling import bad_request
from SoftLayer import CCIManager
from SoftLayer.exceptions import SoftLayerAPIError

from core import api
from services.compute import compute_dispatcher as disp

# This comes from Horizon. I wonder if there's a better place to get it.
POWER_STATES = {
    "NO STATE": 0,
    "RUNNING": 1,
    "BLOCKED": 2,
    "PAUSED": 3,
    "SHUTDOWN": 4,
    "SHUTOFF": 5,
    "CRASHED": 6,
    "SUSPENDED": 7,
    "FAILED": 8,
    "BUILDING": 9,
}

SERVER_STATUSES = [
    'ACTIVE', 'BUILD', 'DELETED', 'ERROR', 'HARD_REBOOT', 'PASSWORD', 'PAUSED',
    'REBOOT', 'REBUILD', 'RESCUE', 'RESIZE', 'REVERT_RESIZE', 'SHUTOFF',
    'SUSPENDED', 'UNKNOWN', 'VERIFY_RESIZE'
]


class SLComputeV2Servers(object):
    def on_get(self, req, resp):
        client = api.config['sl_client']
        cci = CCIManager(client)

        params = {
            'mask': get_virtual_guest_mask(),
        }

        instances = cci.list_instances(**params)

        results = []

        for instance in instances:
            id = instance['id']
            results.append({
                'id': id,
                'links': [
                    {
                        'href': disp.get_endpoint_url('v2_server',
                                                      server_id=id),
                        'rel': 'self',
                    }
                ],
                'name': instance['hostname'],
            })

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(results)


class SLComputeV2Server(object):
    def on_get(self, req, resp, server_id):
        client = api.config['sl_client']
        cci = CCIManager(client)

        params = {
            'id': server_id,
            'mask': get_virtual_guest_mask(),
        }

        try:
            instance = cci.get_instance(**params)
        except SoftLayerAPIError:
            resp.status = falcon.HTTP_404
            resp.body = json.dumps({'itemNotFound': {
                'message':
                'Instance could not be found'}})
            return None

        results = get_server_details_dict(instance)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'server': results})

    def delete(self, tenant_id, instance_id):
        client = api.config['sl_client']
        cci = CCIManager(client)

        cci.cancel_instance(instance_id)
        return {}, 204


def get_server_details_dict(instance):
    image_id = lookup(instance, 'blockDeviceTemplateGroup', 'globalIdentifier')
    tenant_id = instance['accountId']

    # TODO - Don't hardcode this flavor ID'
    flavor_url = disp.get_endpoint_url('v2_flavor', flavor_id=1)
    server_url = disp.get_endpoint_url('v2_server', server_id=instance['id'])

    task_state = None
    transaction = lookup(instance, 'activeTransaction', 'transactionStatus',
                         'transaction_name')

    if 'CLOUD_INSTANCE_NETWORK_RECLAIM' == transaction:
        task_state = 'deleting'

    power_state = 0

    if instance['powerState']['keyName'] in POWER_STATES:
        power_state = POWER_STATES[instance['powerState']['keyName']]

    status = instance['powerState']['keyName']

    if 'RUNNING' == status:
        status = 'ACTIVE'
    elif 'HALTED' == status:
        status = 'SHUTOFF'
        power_state = POWER_STATES['SHUTDOWN']
    elif status not in SERVER_STATUSES and instance.get('provisionDate'):
        status = 'ACTIVE'

    addresses = {}
    if instance.get('primaryBackendIpAddress'):
        addresses['private'] = [{
            'addr': instance.get('primaryBackendIpAddress'),
            'version': 4,
        }]

    if instance.get('primaryIpAddress'):
        addresses['public'] = [{
            'addr': instance.get('primaryIpAddress'),
            'version': 4,
        }]

    results = {
        'id': instance['id'],
        'accessIPv4': '',
        'accessIPv6': '',
        'addresses': addresses,
        'created': instance['createDate'],
        # TODO - Do I need to run this through isoformat()?
        'flavor': {
            # TODO - Make this realistic
            'id': '1',
            'links': [
                {
                    'href': flavor_url,
                    'rel': 'bookmark',
                },
            ],
        },
        'hostId': instance['id'],
        'links': [
            {
                'href': server_url,
                'rel': 'self',
            }
        ],
        'name': instance['hostname'],
        'OS-EXT-AZ:availability_zone': lookup(instance, 'datacenter', 'id'),
        'OS-EXT-STS:power_state': power_state,
        'OS-EXT-STS:task_state': task_state,
        'OS-EXT-STS:vm_state': instance['status']['keyName'],
        'security_groups': [{'name': 'default'}],
        'status': status,
        'tenant_id': tenant_id,
        'updated': instance['modifyDate'],
    }

    if image_id:
        results['image'] = {
            'id': image_id,
            'links': [
                {
                    'href': disp.get_endpoint_url('v2_image',
                                                  image_id=image_id),
                    'rel': 'self',
                },
            ],
        }

    return results


def get_virtual_guest_mask():
    mask = [
        'id',
        'accountId',
        'hostname',
        'createDate',
        'blockDeviceTemplateGroup',
        'datacenter',
        'maxMemory',
        'maxCpu',
        'status',
        'powerState',
        'activeTransaction[transactionStatus]',
        'primaryIpAddress',
        'primaryBackendIpAddress',
        'modifyDate',
        'provisionDate',
    ]

    return 'mask[%s]' % ','.join(mask)
        