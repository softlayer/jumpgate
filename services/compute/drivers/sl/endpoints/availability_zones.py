import json

from SoftLayer import CCIManager

from core import api
from services.common.nested_dict import lookup


class SLComputeV2AvailabilityZones(object):
    def on_get(self, req, resp, tenant_id):
        client = api.config['sl_client']
        cci = CCIManager(client)

        all_options = cci.get_create_options()

        results = []
        # Load and sort all data centers
        for option in all_options['datacenters']:
            name = lookup(option, 'template', 'datacenter', 'name')

            results.append({'zoneState': {'available': True}, 'hosts': None,
                            'zoneName': name})
        results = sorted(results, key=lambda x: x['zoneName'])

        resp.body = json.dumps({'availabilityZoneInfo': results})
