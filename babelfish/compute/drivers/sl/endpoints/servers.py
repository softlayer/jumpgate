import json
import falcon

from SoftLayer import CCIManager, SshKeyManager, SoftLayerAPIError

from babelfish.common.nested_dict import lookup
from babelfish.shared.drivers.sl.errors import convert_errors
from babelfish.common.error_handling import bad_request, duplicate
from babelfish.compute import compute_dispatcher as disp
from .flavors import FLAVORS

# This comes from Horizon. I wonder if there's a better place to get it.
OPENSTACK_POWER_MAP = {
    "NO STATE": 0,
    "RUNNING": 1,
    "BLOCKED": 2,
    "PAUSED": 3,
    "SHUTDOWN": 4,
    "SHUTOFF": 5,
    "CRASHED": 6,
    "SUSPENDED": 7,
}


class SLComputeV2ServerAction(object):
    @convert_errors
    def on_post(self, req, resp, tenant_id, instance_id):
        body = json.loads(req.stream.read().decode())

        if len(body) == 0:
            return bad_request(resp, message="Malformed request body")

        vg_client = req.env['sl_client']['Virtual_Guest']

        if 'pause' in body or 'suspend' in body:
            try:
                vg_client.pause(id=instance_id)
            except SoftLayerAPIError as e:
                if 'Unable to pause instance' in e.faultString:
                    return duplicate(resp, e.faultString)
                raise
            resp.status = falcon.HTTP_202
            return
        elif 'unpause' in body or 'resume' in body:
            vg_client.resume(id=instance_id)
            resp.status = falcon.HTTP_202
            return
        elif 'reboot' in body:
            if body['reboot'].get('type') == 'SOFT':
                vg_client.rebootSoft(id=instance_id)
            elif body['reboot'].get('type') == 'HARD':
                vg_client.rebootHard(id=instance_id)
            else:
                vg_client.rebootDefault(id=instance_id)
            resp.status = falcon.HTTP_202
            return
        elif 'os-stop' in body:
            vg_client.powerOff(id=instance_id)
            resp.status = falcon.HTTP_202
            return
        elif 'os-start' in body:
            vg_client.powerOn(id=instance_id)
            resp.status = falcon.HTTP_202
            return
        elif 'createImage' in body:
            template = {'name': body['createImage']['name'],
                        'volumes': body['createImage']['name']}
            vg_client.captureImage(template, id=instance_id)
            resp.status = falcon.HTTP_202
            return
        elif 'os-getConsoleOutput' in body:
            resp.status = falcon.HTTP_501
            return

        return bad_request(resp,
                           message="There is no such action: %s" %
                           list(body.keys()), code=400)


class SLComputeV2Servers(object):
    @convert_errors
    def on_get(self, req, resp, tenant_id):
        client = req.env['sl_client']
        cci = CCIManager(client)

        params = get_list_params(req)

        sl_instances = cci.list_instances(**params)
        if not isinstance(sl_instances, list):
            sl_instances = [sl_instances]

        results = []
        for instance in sl_instances:
            results.append({
                'id': instance['id'],
                'links': [
                    {
                        'href': disp.get_endpoint_url(req, 'v2_server',
                                                      server_id=id),
                        'rel': 'self',
                    }
                ],
                'name': instance['hostname'],
            })

        resp.status = falcon.HTTP_200
        resp.body = {'servers': results}

    @convert_errors
    def on_post(self, req, resp, tenant_id):
        client = req.env['sl_client']
        body = json.loads(req.stream.read().decode())
        flavor_id = body['server'].get('flavorRef')
        if flavor_id not in FLAVORS:
            return bad_request(resp, 'Flavor could not be found')

        flavor = FLAVORS[flavor_id]

        ssh_keys = []
        key_name = body['server'].get('key_name')
        if key_name:
            sshkey_mgr = SshKeyManager(client)
            keys = sshkey_mgr.list_keys(label=key_name)
            if len(keys) == 0:
                return bad_request(resp, 'KeyPair could not be found')
            ssh_keys.append(keys[0]['id'])

        private_network_only = False
        networks = lookup(body, 'server', 'networks')
        if networks:
            # Make sure they're valid networks
            if not all([network['uuid'] in ['public', 'private']
                        in network for network in networks]):
                return bad_request(resp, message='Invalid network')

            # Find out if it's private only
            if not any([network['uuid'] == 'public'
                        in network for network in networks]):
                private_network_only = True

        user_data = {}
        if lookup(body, 'metadata'):
            user_data = lookup(body, 'metadata')

        cci = CCIManager(client)

        payload = {
            'hostname': body['server']['name'],
            'domain': 'babelfish.com',  # TODO - Don't hardcode this
            'cpus': flavor['cpus'],
            'memory': flavor['ram'],
            'hourly': True,  # TODO - How do we set this accurately?
            # 'datacenter' => ['name' => $datacenter],
            'image_id': body['server']['imageRef'],
            'ssh_keys': ssh_keys,
            'private': private_network_only,
            'userdata': json.dumps(user_data),
        }

        try:
            new_instance = cci.create_instance(**payload)
        except ValueError as e:
            return bad_request(resp, message=str(e))

        resp.set_header('x-compute-request-id', 'create')
        resp.status = falcon.HTTP_202
        resp.body = {'server': {
            'id': new_instance['id'],
            'links': [{
                'href': disp.get_endpoint_url(req, 'v2_server',
                                              instance_id=new_instance['id']),
                'rel': 'self'}],
            'adminPass': '',
        }}


def get_list_params(req):
    _filter = {
        'virtualGuests': {
            'createDate': {
                'operation': 'orderBy',
                'options': [{'name': 'sort', 'value': ['ASC']}],
            }
        }
    }

    if req.get_param('marker') is not None:
        _filter['virtualGuests']['id'] = {
            'operation': '> %s' % req.get_param('marker')
        }

    if req.get_param('image') is not None:
        # TODO: filter on image in URL format
        pass

    if req.get_param('flavor') is not None:
        # TODO: filter on flavor in URL format
        pass

    if req.get_param('status') is not None:
        # TODO: filter on status
        pass

    if req.get_param('changes-since') is not None:
        # TODO: filter on changes-since
        pass

    if req.get_param('ip') is not None:
        _filter['virtualGuests']['primaryIpAddress'] = {
            'operation': req.get_param('ip')
        }

    if req.get_param('ip6') is not None:
        # TODO: filter on ipv6 address
        pass

    if req.get_param('name') is not None:
        _filter['virtualGuests']['hostname'] = {
            'operation': '~ %s' % req.get_param('name'),
        }

    limit = None
    if req.get_param('limit') is not None:
        try:
            limit = int(req.get_param('limit'))
        except ValueError:
            pass

    return {
        'limit': limit,
        'filter': _filter,
        'mask': get_virtual_guest_mask(),
    }


class SLComputeV2ServersDetail(object):
    @convert_errors
    def on_get(self, req, resp, tenant_id=None):
        client = req.env['sl_client']
        cci = CCIManager(client)

        params = get_list_params(req)

        sl_instances = cci.list_instances(**params)
        if not isinstance(sl_instances, list):
            sl_instances = [sl_instances]

        results = []
        for instance in sl_instances:
            results.append(get_server_details_dict(req, instance))

        resp.status = falcon.HTTP_200
        resp.body = {'servers': results}


class SLComputeV2Server(object):
    @convert_errors
    def on_get(self, req, resp, tenant_id, server_id):
        client = req.env['sl_client']
        cci = CCIManager(client)

        instance = cci.get_instance(id=server_id,
                                    mask=get_virtual_guest_mask())

        results = get_server_details_dict(req, instance)

        resp.body = {'server': results}

    @convert_errors
    def on_delete(self, req, resp, tenant_id, server_id):
        client = req.env['sl_client']
        cci = CCIManager(client)

        # TODO: ADD TENANT CHECK

        try:
            cci.cancel_instance(server_id)
        except SoftLayerAPIError as e:
            if 'active transaction' in e.faultString:
                return bad_request(
                    resp,
                    message='Can not cancel an instance when there is already'
                    ' an active transaction', code=409)
            raise
        resp.status = falcon.HTTP_204

    @convert_errors
    def on_put(self, req, resp, tenant_id, server_id):
        client = req.env['sl_client']
        cci = CCIManager(client)
        body = json.loads(req.stream.read().decode())

        # TODO: ADD TENANT CHECK

        if 'name' in lookup(body, 'server'):
            if lookup(body, 'server', 'name').strip() == '':
                return bad_request(resp, message='Server name is blank')

            cci.edit(server_id, hostname=lookup(body, 'server', 'name'))

        instance = cci.get_instance(id=server_id,
                                    mask=get_virtual_guest_mask())

        results = get_server_details_dict(req, instance)
        resp.body = {'server': results}


def get_server_details_dict(req, instance):
    image_id = lookup(instance, 'blockDeviceTemplateGroup', 'globalIdentifier')
    tenant_id = instance['accountId']

    # TODO - Don't hardcode this flavor ID
    flavor_url = disp.get_endpoint_url(req, 'v2_flavor', flavor_id=1)
    server_url = disp.get_endpoint_url(req, 'v2_server',
                                       server_id=instance['id'])

    task_state = None
    transaction = lookup(
        instance, 'activeTransaction', 'transactionStatus', 'name')

    if transaction and 'RECLAIM' in transaction:
        task_state = 'deleting'
    else:
        task_state = transaction

    # Map SL Power States to OpenStack Power States
    power_state = 0
    status = 'UNKNOWN'

    sl_power_state = instance['powerState']['keyName']
    if sl_power_state == 'RUNNING':
        if transaction or not instance.get('provisionDate'):
            status = 'BUILD'
            power_state = OPENSTACK_POWER_MAP['BLOCKED']
        else:
            status = 'ACTIVE'
            power_state = OPENSTACK_POWER_MAP['RUNNING']
    elif sl_power_state == 'PAUSED':
        status = 'PAUSED'
        power_state = OPENSTACK_POWER_MAP[sl_power_state]
    elif sl_power_state in OPENSTACK_POWER_MAP:
        power_state = OPENSTACK_POWER_MAP[sl_power_state]
    elif sl_power_state == 'HALTED':
        status = 'BUILD'
        power_state = OPENSTACK_POWER_MAP['BLOCKED']

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

    # TODO - Don't hardcode this
    image_name = ''

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
        'image_name': image_name,
    }

    # OpenStack only supports having one SSH Key assigned to an instance
    if instance['sshKeys']:
        results['key_name'] = instance['sshKeys'][0]['label']

    if image_id:
        results['image'] = {
            'id': image_id,
            'links': [
                {
                    'href': disp.get_endpoint_url(req, 'v2_image',
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
        'sshKeys',
    ]

    return 'mask[%s]' % ','.join(mask)
