import json
from services.common.error_handling import bad_request, not_found

from services.compute import compute_dispatcher as disp

FLAVORS = {
    '1': {
        'id': '1',
        'name': '1 vCPU, 1GB ram, 25GB',
        'ram': 1024,
        'disk': 25,
        'cpus': 1,
    },
    '2': {
        'id': '2',
        'name': '1 vCPU, 1GB ram, 100GB',
        'ram': 1024,
        'disk': 100,
        'cpus': 1,
    },
    '3': {
        'id': '3',
        'name': '2 vCPU, 2GB ram, 100GB',
        'ram': 4 * 1024,
        'disk': 100,
        'cpus': 2,
    },
    '4': {
        'id': '4',
        'name': '4 vCPU, 4GB ram, 100GB',
        'ram': 4 * 1024,
        'disk': 100,
        'cpus': 4,
    },
    '5': {
        'id': '5',
        'name': '8 vCPU, 8GB ram, 100GB',
        'ram': 8 * 1024,
        'disk': 100,
        'cpus': 8,
    },
}


class SLComputeV2Flavor(object):
    def on_get(self, req, resp, flavor_id, tenant_id=None):
        if flavor_id not in FLAVORS:
            return not_found(resp, 'Flavor could not be found')

        flavor = get_flavor_details(req, FLAVORS[flavor_id], detail=True)
        resp.body = json.dumps({'flavor': flavor})


class SLComputeV2Flavors(object):
    def on_get(self, req, resp, tenant_id=None):
        flavor_refs = [flavor for flavor_id, flavor in FLAVORS.items()]
        flavor_refs = filter_flavor_refs(req, resp, flavor_refs)
        if flavor_refs is None:
            return
        flavors = [get_flavor_details(req, flavor) for flavor in flavor_refs]
        resp.body = json.dumps({'flavors': flavors})


class SLComputeV2FlavorsDetail(object):
    def on_get(self, req, resp, tenant_id=None):
        flavor_refs = [flavor for flavor_id, flavor in FLAVORS.items()]
        flavor_refs = filter_flavor_refs(req, resp, flavor_refs)
        if flavor_refs is None:
            return
        flavors = [get_flavor_details(req, flavor, detail=True)
                   for flavor in flavor_refs]
        resp.body = json.dumps({'flavors': flavors})


def filter_flavor_refs(req, resp, flavor_refs):
    if req.get_param('marker'):
        marker = req.get_param('marker')
        flavor_refs = [f for f in flavor_refs if f['id'] > marker]

    if req.get_param('minDisk'):
        try:
            min_disk = int(req.get_param('minDisk'))
            flavor_refs = [f for f in flavor_refs
                           if f['disk'] >= min_disk]
        except ValueError:
            bad_request(resp, message="Invalid minDisk parameter.")
            return

    if req.get_param('minRam'):
        try:
            min_ram = int(req.get_param('minRam'))
            flavor_refs = [f for f in flavor_refs if f['ram'] >= min_ram]
        except ValueError:
            bad_request(resp, message="Invalid minRam parameter.")
            return

    if req.get_param('limit'):
        try:
            limit = int(req.get_param('limit'))
            flavor_refs = flavor_refs[:limit]
        except ValueError:
            bad_request(resp, message="Invalid limit parameter.")
            return

    return flavor_refs


def get_flavor_details(req, flavor_ref, detail=False):
    flavor = {
        'id': flavor_ref['id'],
        'links': [
            {
                'href': disp.get_endpoint_url(req,
                                              'v2_flavor',
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
        flavor['swap'] = ''
        flavor['rxtx_factor'] = 1
        flavor['os-flavor-access:is_public'] = True
        flavor['OS-FLV-EXT-DATA:ephemeral'] = 0
        flavor['OS-FLV-DISABLED:disabled'] = False

    return flavor
