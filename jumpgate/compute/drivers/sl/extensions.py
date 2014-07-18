from jumpgate.common import error_handling

EXTENSIONS = {
    'os-availability-zone': {
        'alias': 'os-availability-zone',
        'description': '''Availability-zone support''',
        'links': [],
        'name': 'AvailabilityZone',
        'namespace': 'http://docs.openstack.org/compute/ext/availabilityzone/'
                     'api/v1.1',
        'updated': '2012-12-21T00:00:00+00:00',
        # TODO(imkarrer) Added availability zone, need to return real value
        'availability_zone': {'Hosts': None},
    },
}


class ExtensionsV2(object):
    def on_get(self, req, resp, tenant_id):
        resp.body = {'extensions': EXTENSIONS.values()}


class ExtensionV2(object):
    def on_get(self, req, resp, tenant_id, alias):
        if alias not in EXTENSIONS:
            return error_handling.not_found(
                resp, 'No extension exists with given alias.')

        resp.body = {'extension': EXTENSIONS[alias]}
