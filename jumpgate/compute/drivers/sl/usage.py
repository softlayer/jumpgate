import datetime

import SoftLayer

from jumpgate.compute.drivers.sl import servers


class UsageV2(object):
    def on_get(self, req, resp, tenant_id, target_id):
        client = req.env['sl_client']
        cci = SoftLayer.VSManager(client)
        start_time = datetime.datetime.now() + datetime.timedelta(hours=-1)
        usage = {
            'server_usages': [],
            'start': start_time.isoformat(),
            'stop': datetime.datetime.now().isoformat(),
            'tenant_id': target_id,
            'total_hours': 0.0,
            'total_local_gb_usage': 0.0,
            'total_memory_mb_usage': 0.0,
            'total_vcpus_usage': 0.0,
        }

        params = {
            'mask': servers.get_virtual_guest_mask(),
        }

        for instance in cci.list_instances(**params):
            server_dict = {
                'ended_at': None,
                'flavor': 'custom',
                'hours': 0.0,
                'instance_id': instance['id'],
                'local_gb': 1,
                'memory_mb': instance['maxMemory'],
                'name': instance['hostname'],
                'started_at': instance.get('provisionDate'),
                'state': instance['status']['keyName'].lower(),
                'tenant_id': target_id,
                'uptime': 3600,
                'vcpus': instance['maxCpu'],
            }
            usage['total_vcpus_usage'] += instance['maxCpu']
            usage['total_memory_mb_usage'] += instance['maxMemory']
            usage['server_usages'].append(server_dict)

        resp.body = {'tenant_usage': usage}
