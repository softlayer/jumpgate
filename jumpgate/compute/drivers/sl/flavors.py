import logging

from jumpgate.common import error_handling


LOG = logging.getLogger(__name__)


class FlavorV2(object):
    def __init__(self, app, flavors):
        self.app = app
        self.flavors = flavors

    def on_get(self, req, resp, flavor_id, tenant_id=None):
        for flavor in self.flavors:
            if str(flavor_id) == flavor['id']:
                flavor = get_flavor_details(self.app, req,
                                            flavor, detail=True)
                resp.body = {'flavor': flavor}
                return
        return error_handling.not_found(resp, 'Flavor could not be found')


class FlavorsV2(object):
    def __init__(self, app, flavors):
        self.app = app
        self.flavors = flavors

    def on_get(self, req, resp, tenant_id=None):
        '''Returns details of all available flavors

        '''
        flavor_refs = filter_flavor_refs(req, resp, self.flavors)
        if flavor_refs is None:
            return
        flavors = [get_flavor_details(self.app, req, flavor)
                   for flavor in flavor_refs]
        resp.body = {'flavors': flavors}


class FlavorsDetailV2(object):
    def __init__(self, app, flavors):
        self.app = app
        self.flavors = flavors

    def on_get(self, req, resp, tenant_id=None):
        '''Returns details of all available flavors after filtering

        certain flavors out based on the parameters set

        '''
        flavor_refs = filter_flavor_refs(req, resp, self.flavors)
        if flavor_refs is None:
            return
        flavors = [get_flavor_details(self.app, req, flavor, detail=True)
                   for flavor in flavor_refs]
        resp.body = {'flavors': flavors}


def filter_flavor_refs(req, resp, flavor_refs):
    if req.get_param('marker') is not None:
        marker = req.get_param('marker')
        flavor_refs = [f for f in flavor_refs if str(f['id']) > marker]

    if req.get_param('minDisk') is not None:
        try:
            min_disk = int(req.get_param('minDisk'))
            flavor_refs = [f for f in flavor_refs
                           if f['disk'] >= min_disk]
        except ValueError:
            error_handling.bad_request(resp,
                                       message="Invalid minDisk parameter.")
            return

    if req.get_param('minRam') is not None:
        try:
            min_ram = int(req.get_param('minRam'))
            flavor_refs = [f for f in flavor_refs if f['ram'] >= min_ram]
        except ValueError:
            error_handling.bad_request(resp,
                                       message="Invalid minRam parameter.")
            return

    if req.get_param('limit') is not None:
        try:
            limit = int(req.get_param('limit'))
            flavor_refs = flavor_refs[:limit]
        except ValueError:
            error_handling.bad_request(resp,
                                       message="Invalid limit parameter.")
            return

    return flavor_refs


def get_flavor_details(app, req, flavor_ref, detail=False):
    flavor = {
        'id': flavor_ref['id'],
        'links': [
            {
                'href': app.get_endpoint_url('compute', req, 'v2_flavor',
                                             flavor_id=flavor_ref['id']),
                'rel': 'self',
            }
        ],
        'name': flavor_ref['name'],

    }
    if detail:
        flavor['disk'] = flavor_ref['disk']
        flavor['ram'] = flavor_ref['ram']
        flavor['vcpus'] = flavor_ref['cpus']
        flavor['OS-FLV-DISK-TYPE:disk_type'] = flavor_ref['disk-type']
        flavor['swap'] = ''
        flavor['rxtx_factor'] = 1
        flavor['os-flavor-access:is_public'] = True
        flavor['OS-FLV-EXT-DATA:ephemeral'] = 0
        flavor['OS-FLV-DISABLED:disabled'] = False
        try:
            flavor['portspeed'] = flavor_ref['portspeed']
        except Exception:
            pass

    return flavor
