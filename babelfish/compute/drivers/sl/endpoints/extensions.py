

class SLComputeV2Extensions(object):
    def on_get(self, req, resp, tenant_id):
        resp.body = {'extensions': [
            {
                'alias': 'os-availability-zone',
                'description': '''1. Add availability_zone to the Create Server v1.1 API.
2. Add availability zones describing.
''',
                'links': [],
                'name': 'AvailabilityZone',
                'namespace': 'http://docs.openstack.org/compute/ext/availabilityzone/api/v1.1',
                'updated': '2012-12-21T00:00:00+00:00'
            },
        ]}
