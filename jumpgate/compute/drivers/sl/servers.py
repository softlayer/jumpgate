import json
import logging
import re

import SoftLayer


from jumpgate.common import config
from jumpgate.common import error_handling
from jumpgate.common import utils


LOG = logging.getLogger(__name__)


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


class ServerActionV2(object):
    def __init__(self, app, flavors):
        self.app = app
        self.flavors = flavors

    def on_post(self, req, resp, tenant_id, instance_id):
        body = json.loads(req.stream.read().decode())

        if len(body) == 0:
            return error_handling.bad_request(resp,
                                              message="Malformed request body")

        vg_client = req.env['sl_client']['Virtual_Guest']
        cci = SoftLayer.VSManager(req.env['sl_client'])

        try:
            instance_id = int(instance_id)
        except Exception:
            return error_handling.not_found(resp,
                                            "Invalid instance ID specified.")

        instance = cci.get_instance(instance_id)

        if 'pause' in body or 'suspend' in body:
            try:
                vg_client.pause(id=instance_id)
            except SoftLayer.SoftLayerAPIError as e:
                if 'Unable to pause instance' in e.faultString:
                    return error_handling.duplicate(resp, e.faultString)
                raise
            resp.status = 202
            return
        elif 'unpause' in body or 'resume' in body:
            vg_client.resume(id=instance_id)
            resp.status = 202
            return
        elif 'reboot' in body:
            if body['reboot'].get('type') == 'SOFT':
                vg_client.rebootSoft(id=instance_id)
            elif body['reboot'].get('type') == 'HARD':
                vg_client.rebootHard(id=instance_id)
            else:
                vg_client.rebootDefault(id=instance_id)
            resp.status = 202
            return
        elif 'os-stop' in body:
            vg_client.powerOff(id=instance_id)
            resp.status = 202
            return
        elif 'os-start' in body:
            vg_client.powerOn(id=instance_id)
            resp.status = 202
            return
        elif 'createImage' in body:
            image_name = body['createImage']['name']
            disks = []

            for disk in filter(lambda x: x['device'] == '0',
                               instance['blockDevices']):
                disks.append(disk)

            try:
                vg_client.createArchiveTransaction(
                    image_name,
                    disks,
                    "Auto-created by OpenStack compatibility layer",
                    id=instance_id,
                )
                # Workaround for not having an image guid until the image is
                # fully created. TODO(nbeitenmiller): Fix this
                cci.wait_for_transaction(instance_id, 300)
                _filter = {
                    'privateBlockDeviceTemplateGroups': {
                        'name': {'operation': image_name},
                        'createDate': {
                            'operation': 'orderBy',
                            'options': [{'name': 'sort', 'value': ['DESC']}],
                        }
                    }}

                acct = req.env['sl_client']['Account']
                matching_image = acct.getPrivateBlockDeviceTemplateGroups(
                    mask='id, globalIdentifier', filter=_filter, limit=1)
                image_guid = matching_image.get('globalIdentifier')

                url = self.app.get_endpoint_url('image', req, 'v2_image',
                                                image_guid=image_guid)

                resp.status = 202
                resp.set_header('location', url)
            except SoftLayer.SoftLayerAPIError as e:
                error_handling.compute_fault(resp, e.faultString)
            return
        elif 'os-getConsoleOutput' in body:
            resp.status = 501
            return
        elif 'resize' in body:
            flavor_id = int(body['resize'].get('flavorRef'))
            for flavor in self.flavors:
                if str(flavor_id) == flavor['id']:
                    vg_client.setTags('{"flavor_id": ' + str(flavor_id) + '}',
                                      id=instance_id)
                    cci.upgrade(instance_id, cpus=flavor['cpus'],
                                memory=flavor['ram'] / 1024)
                    resp.status = 202
                    return
            return error_handling.bad_request(resp, message="Invalid flavor "
                                              "id in the request body")
        elif 'confirmResize' in body:
            resp.status = 204
            return

        return error_handling.bad_request(
            resp,
            message="There is no such action: %s" % list(body.keys()),
            code=400)


class ServersV2(object):
    def __init__(self, app, flavors):
        self.app = app
        self.flavors = flavors

    def on_get(self, req, resp, tenant_id):
        client = req.env['sl_client']
        cci = SoftLayer.VSManager(client)

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
                        'href': self.app.get_endpoint_url(
                            'compute', req, 'v2_server', server_id=id),
                        'rel': 'self',
                    }
                ],
                'name': instance['hostname'],
            })

        resp.status = 200
        resp.body = {'servers': results}

    def on_post(self, req, resp, tenant_id):
        payload = {}
        client = req.env['sl_client']
        body = json.loads(req.stream.read().decode())

        payload['hostname'] = body['server']['name']
        payload['domain'] = config.CONF['default_domain'] or 'jumpgate.com'
        payload['image_id'] = body['server']['imageRef']

        # TODO(kmcdonald) - How do we set this accurately?
        payload['hourly'] = True

        networks = utils.lookup(body, 'server', 'networks')
        cci = SoftLayer.VSManager(client)

        try:
            self._handle_flavor(payload, body)
            self._handle_sshkeys(payload, body, client)
            self._handle_user_data(payload, body)
            self._handle_datacenter(payload, body)
            if networks:
                self._handle_network(payload, client, networks)
            new_instance = cci.create_instance(**payload)
        except Exception as e:
            return error_handling.bad_request(resp, message=str(e))

        # This should be the first tag that the VS set. Adding any more tags
        # will replace this tag
        try:
            flavor_id = int(body['server'].get('flavorRef'))
            vs = client['Virtual_Guest']
            vs.setTags('{"flavor_id": ' + str(flavor_id) + '}',
                       id=new_instance['id'])
        except Exception:
            pass

        resp.set_header('x-compute-request-id', 'create')
        resp.status = 202
        resp.body = {'server': {
            # Casted to string to make tempest pass
            'id': str(new_instance['id']),
            'links': [{
                'href': self.app.get_endpoint_url(
                    'compute', req, 'v2_server',
                    instance_id=new_instance['id']),
                'rel': 'self'}],
            'adminPass': '',
            # TODO(imkarrer) - Added security_groups to make tempest pass, need real groups  # noqa
            'security_groups': []
        }}

    def _handle_flavor(self, payload, body):
        flavor_id = int(body['server'].get('flavorRef'))
        for flavor in self.flavors:
            if str(flavor_id) == flavor['id']:
                payload['cpus'] = flavor['cpus']
                payload['memory'] = flavor['ram']
                payload['local_disk'] = (False if flavor['disk-type'] == 'SAN'
                                         else True)
                try:
                    port_speed = flavor['portspeed']
                    payload['nic_speed'] = port_speed
                except Exception:
                    # If port speed is not specified, it is left to SoftLayer
                    # to provide the 'default' port speed
                    pass
                return
        raise Exception('Flavor could not be found')

    def _handle_sshkeys(self, payload, body, client):
        ssh_keys = []
        key_name = body['server'].get('key_name')
        if key_name:
            sshkey_mgr = SoftLayer.SshKeyManager(client)
            keys = sshkey_mgr.list_keys(label=key_name)
            if len(keys) == 0:
                raise Exception('KeyPair could not be found')
            ssh_keys.append(keys[0]['id'])
        payload['ssh_keys'] = ssh_keys

    def _handle_user_data(self, payload, body):
        user_data = {}
        if utils.lookup(body, 'server', 'metadata'):
            user_data['metadata'] = utils.lookup(body, 'server', 'metadata')
        if utils.lookup(body, 'server', 'user_data'):
            user_data['user_data'] = utils.lookup(body, 'server', 'user_data')
        if utils.lookup(body, 'server', 'personality'):
            user_data['personality'] = utils.lookup(body,
                                                    'server',
                                                    'personality')
        payload['userdata'] = json.dumps(user_data)

    def _handle_datacenter(self, payload, body):
        datacenter = (utils.lookup(body, 'server', 'availability_zone')
                      or config.CONF['compute']['default_availability_zone'])
        if not datacenter:
            raise Exception('availability_zone missing')
        payload['datacenter'] = datacenter

    def _handle_network(self, payload, client, networks):
        """Set the network part for the payload. Support the following:

        1) --net-id=public

        2) --net-id=private

        3) --net-id=<private id>

        4) --net-id=<private id> --net-id=<public id>
        """

        if len(networks) > 2:
            raise Exception('Too many net-id arguments')

        # support cases of the string 'public' or 'private'
        if networks[0]['uuid'] == 'public':
            if len(networks) > 1:
                raise Exception('Too many net-id arguments. '
                                'Please indicate only "public" or "private"')
            payload['private'] = False
            return
        elif networks[0]['uuid'] == 'private':
            if len(networks) > 1:
                raise Exception('Too many net-id arguments. '
                                'Please indicate only "public" or "private"')
            payload['private'] = True
            return

        private_network_only = True
        try:
            _filter = {
                'networkVlans': {'id': {'operation': int(networks[0]['uuid'])}}
            }
        except Exception:
            raise ValueError('Invalid id format')

        priv_id_valid = (
            client['Account'].getPrivateNetworkVlans(filter=_filter))
        if priv_id_valid:
            payload['private_vlan'] = int(networks[0]['uuid'])
        else:
            raise Exception('Private vlan must be specified first '
                            'or is invalid')

        # if there is another net-id, then it should be a public network
        if len(networks) == 2:
            try:
                _filter = {
                    'networkVlans': {'id': {'operation':
                                            int(networks[1]['uuid'])}}
                }
            except Exception:
                raise ValueError('Invalid id format')
            pub_id_valid = (
                client['Account'].getPublicNetworkVlans(filter=_filter))
            if pub_id_valid:
                payload['public_vlan'] = int(networks[1]['uuid'])
                private_network_only = False
            else:
                raise Exception('Public vlan must be specified second '
                                'or is invalid')

        payload['private'] = private_network_only


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
        # TODO(kmcdonald): filter on image in URL format
        pass

    if req.get_param('flavor') is not None:
        # TODO(kmcdonald): filter on flavor in URL format
        pass

    if req.get_param('status') is not None:
        # TODO(kmcdonald): filter on status
        pass

    if req.get_param('changes-since') is not None:
        # TODO(kmcdonald): filter on changes-since
        pass

    if req.get_param('ip') is not None:
        _filter['virtualGuests']['primaryIpAddress'] = {
            'operation': req.get_param('ip')
        }

    if req.get_param('ip6') is not None:
        # TODO(kmcdonald): filter on ipv6 address
        pass

    name = req.get_param('name') or req.get_param('instance_name')
    if name is not None:
        _filter['virtualGuests']['hostname'] = {'operation': '~ %s' % name}

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


class ServersDetailV2(object):
    def __init__(self, app):
        self.app = app

    def on_get(self, req, resp, tenant_id=None):
        client = req.env['sl_client']
        cci = SoftLayer.VSManager(client)

        params = get_list_params(req)

        sl_instances = cci.list_instances(**params)
        if not isinstance(sl_instances, list):
            sl_instances = [sl_instances]

        results = []
        for instance in sl_instances:
            results.append(
                get_server_details_dict(self.app, req, instance, False))

        resp.status = 200
        resp.body = {'servers': results}


class ServerV2(object):
    def __init__(self, app):
        self.app = app

    def on_get(self, req, resp, tenant_id, server_id):
        client = req.env['sl_client']
        cci = SoftLayer.VSManager(client)

        instance = cci.get_instance(server_id,
                                    mask=get_virtual_guest_mask())

        results = get_server_details_dict(self.app, req, instance, True)

        resp.body = {'server': results}

    def on_delete(self, req, resp, tenant_id, server_id):
        client = req.env['sl_client']
        cci = SoftLayer.VSManager(client)

        try:
            cci.cancel_instance(server_id)
        except SoftLayer.SoftLayerAPIError as e:
            if 'active transaction' in e.faultString:
                return error_handling.bad_request(
                    resp,
                    message='Can not cancel an instance when there is already'
                    ' an active transaction', code=409)
            raise
        resp.status = 204

    def on_put(self, req, resp, tenant_id, server_id):
        client = req.env['sl_client']
        cci = SoftLayer.VSManager(client)
        body = json.loads(req.stream.read().decode())

        if 'name' in utils.lookup(body, 'server'):
            if utils.lookup(body, 'server', 'name').strip() == '':
                return error_handling.bad_request(
                    resp, message='Server name is blank')

            cci.edit(server_id, hostname=utils.lookup(body, 'server', 'name'))

        instance = cci.get_instance(server_id,
                                    mask=get_virtual_guest_mask())

        results = get_server_details_dict(self.app, req, instance, False)
        resp.body = {'server': results}


def get_server_details_dict(app, req, instance, is_list):

    image_id = utils.lookup(instance,
                            'blockDeviceTemplateGroup',
                            'globalIdentifier')
    tenant_id = str(instance['accountId'])

    client = req.env['sl_client']
    vs = client['Virtual_Guest']

    flavor_url = None
    flavor_id = 1

    if is_list:
        tags = vs.getTagReferences(id=instance['id'])
        for tag in tags:
            if 'flavor_id' in tag['tag']['name']:
                try:
                    # Try to parse the flavor id from the tag format
                    # i.e. 'flavor_id: 2'
                    tag_string = tag['tag']['name']

                    flavor_id = int(re.search(r'\d+', tag_string).group())
                    flavor_url = app.get_endpoint_url(
                        'compute', req, 'v2_flavor', flavor_id=flavor_id)
                except Exception:
                    pass

    # Workaround of hardcoded ID for VS's created before flavor-id
    # pushed into tags
    if not flavor_url:
        flavor_url = app.get_endpoint_url(
            'compute', req, 'v2_flavor', flavor_id=1)

    server_url = app.get_endpoint_url(
        'compute', req, 'v2_server', server_id=instance['id'])

    task_state = None
    transaction = utils.lookup(instance,
                               'activeTransaction',
                               'transactionStatus',
                               'name')

    if transaction and any(['RECLAIM' in transaction,
                            'TEAR_DOWN' in transaction]):
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
        power_state = OPENSTACK_POWER_MAP['PAUSED']
    elif sl_power_state in OPENSTACK_POWER_MAP:
        power_state = OPENSTACK_POWER_MAP[sl_power_state]
    elif sl_power_state == 'HALTED' and instance.get('provisionDate'):
        status = 'SHUTOFF'
        power_state = OPENSTACK_POWER_MAP['SHUTOFF']
    elif sl_power_state == 'HALTED':
        status = 'SHUTOFF'
        power_state = OPENSTACK_POWER_MAP['BLOCKED']

    addresses = {}
    if instance.get('primaryBackendIpAddress'):
        addresses['private'] = [{
            'addr': instance.get('primaryBackendIpAddress'),
            'version': 4,
            'OS-EXT-IPS:type': 'fixed',
        }]

    if instance.get('primaryIpAddress'):
        addresses['public'] = [{
            'addr': instance.get('primaryIpAddress'),
            'version': 4,
            'OS-EXT-IPS:type': 'fixed',
        }]

    # TODO(kmcdonald) - Don't hardcode this
    image_name = ''
    # returning None makes tempest fail,
    # conditionally returning empty string for uid and zone
    uid = str(utils.lookup(instance,
                           'billingItem',
                           'orderItem',
                           'order',
                           'userRecordId'))
    if not uid:
        uid = ''
    zone = str(utils.lookup(instance,
                            'datacenter',
                            'id'))
    if not zone:
        zone = ''

    results = {
        'id': str(instance['id']),
        'accessIPv4': '',
        'accessIPv6': '',
        'addresses': addresses,
        'created': instance['createDate'],
        # TODO(nbeitenmiller) - Do I need to run this through isoformat()?
        'flavor': {
            'id': str(flavor_id),
            'links': [
                {
                    'href': flavor_url,
                    'rel': 'bookmark',
                },
            ],
        },
        'hostId': str(instance['id']),
        'links': [
            {
                'href': server_url,
                'rel': 'self',
            }
        ],
        'name': instance['hostname'],
        'OS-EXT-AZ:availability_zone': zone,
        'OS-EXT-STS:power_state': power_state,
        'OS-EXT-STS:task_state': task_state,
        'OS-EXT-STS:vm_state': instance['status']['keyName'],
        'security_groups': [{'name': 'default'}],
        'status': status,
        'tenant_id': tenant_id,
        # NOTE(bodenr): userRecordId accessibility determined by permissions
        # of API caller's user id and api key. Otherwise it will be None
        'user_id': uid,
        'updated': instance['modifyDate'],
        'image_name': image_name,
        # TODO(imkarrer) added to make tempest pass, need real metadata
        'metadata': {}
    }

    # OpenStack only supports having one SSH Key assigned to an instance
    if instance['sshKeys']:
        results['key_name'] = instance['sshKeys'][0]['label']

    if image_id:
        results['image'] = {
            'id': image_id,
            'links': [
                {
                    'href': app.get_endpoint_url(
                        'compute', req, 'v2_image', image_id=image_id),
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
        'billingItem.orderItem.order.userRecordId'
    ]

    return 'mask[%s]' % ','.join(mask)
