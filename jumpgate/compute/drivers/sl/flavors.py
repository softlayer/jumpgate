from jumpgate.common.error_handling import bad_request, not_found
import base64
import re

FLAVORS = {
    1: {
        'id': '1',
        'name': '1 vCPU, 1GB ram, 25GB, local',
        'ram': 1024,
        'disk': 25,
        'disk-type': 'Local',
        'cpus': 1,
    },
    2: {
        'id': '2',
        'name': '1 vCPU, 1GB ram, 100GB, local',
        'ram': 1024,
        'disk': 100,
        'disk-type': 'Local',
        'cpus': 1,
    },
    3: {
        'id': '3',
        'name': '2 vCPU, 2GB ram, 100GB, local',
        'ram': 2 * 1024,
        'disk': 100,
        'disk-type': 'Local',
        'cpus': 2,
    },
    4: {
        'id': '4',
        'name': '4 vCPU, 4GB ram, 100GB, local',
        'ram': 4 * 1024,
        'disk': 100,
        'disk-type': 'Local',
        'cpus': 4,
    },
    5: {
        'id': '5',
        'name': '8 vCPU, 8GB ram, 100GB, local',
        'ram': 8 * 1024,
        'disk': 100,
        'disk-type': 'Local',
        'cpus': 8,
    },
    11: {
        'id': '11',
        'name': '1 vCPU, 1GB ram, 25GB, SAN',
        'ram': 1024,
        'disk': 25,
        'disk-type': 'SAN',
        'cpus': 1,
    },
    12: {
        'id': '12',
        'name': '1 vCPU, 1GB ram, 100GB, SAN',
        'ram': 1024,
        'disk': 100,
        'disk-type': 'SAN',
        'cpus': 1,
    },
    13: {
        'id': '13',
        'name': '2 vCPU, 2GB ram, 100GB, SAN',
        'ram': 2 * 1024,
        'disk': 100,
        'disk-type': 'SAN',
        'cpus': 2,
    },
    14: {
        'id': '14',
        'name': '4 vCPU, 4GB ram, 100GB, SAN',
        'ram': 4 * 1024,
        'disk': 100,
        'disk-type': 'SAN',
        'cpus': 4,
    },
    15: {
        'id': '15',
        'name': '8 vCPU, 8GB ram, 100GB, SAN',
        'ram': 8 * 1024,
        'disk': 100,
        'disk-type': 'SAN',
        'cpus': 8,
    },
}


def encode_tob64_id(name):
    return base64.b64encode((name.replace(" ", "")).replace(",", ":"))


def decode_fromb64_string(idstr):
    return base64.b64decode(idstr)


def set_flavors_base64_id():
    for flavor_id, flavor in FLAVORS.items():
        flavor['id'] = encode_tob64_id(flavor['name'])


# Set flavor '1' as the default
FLAVORS[None] = FLAVORS[1]
# Encode flavor ids
set_flavors_base64_id()


class FlavorV2(object):
    def __init__(self, app):
        self.app = app

    def on_get(self, req, resp, flavor_id, tenant_id=None):
        try:
            flavor_id = int(flavor_id)
        except ValueError:
            return not_found(resp, 'Flavor could not be found')

        if flavor_id not in FLAVORS:
            return not_found(resp, 'Flavor could not be found')

        flavor = get_flavor_details(self.app, req, FLAVORS[flavor_id],
                                    detail=True)
        resp.body = {'flavor': flavor}


class FlavorsV2(object):
    def __init__(self, app):
        self.app = app

    def on_get(self, req, resp, tenant_id=None):
        flavor_refs = filter_flavor_refs(req, resp, get_listing_flavors())
        if flavor_refs is None:
            return
        flavors = [get_flavor_details(self.app, req, flavor)
                   for flavor in flavor_refs]
        resp.body = {'flavors': flavors}


class FlavorsDetailV2(object):
    def __init__(self, app):
        self.app = app

    def on_get(self, req, resp, tenant_id=None):
        flavor_refs = get_listing_flavors()
        flavor_refs = filter_flavor_refs(req, resp, flavor_refs)
        if flavor_refs is None:
            return
        flavors = [get_flavor_details(self.app, req, flavor, detail=True)
                   for flavor in flavor_refs]
        resp.body = {'flavors': flavors}


def get_listing_flavors():
    return [flavor for flavor_id, flavor in FLAVORS.items() if flavor_id]


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
            bad_request(resp, message="Invalid minDisk parameter.")
            return

    if req.get_param('minRam') is not None:
        try:
            min_ram = int(req.get_param('minRam'))
            flavor_refs = [f for f in flavor_refs if f['ram'] >= min_ram]
        except ValueError:
            bad_request(resp, message="Invalid minRam parameter.")
            return

    if req.get_param('limit') is not None:
        try:
            limit = int(req.get_param('limit'))
            flavor_refs = flavor_refs[:limit]
        except ValueError:
            bad_request(resp, message="Invalid limit parameter.")
            return

    return flavor_refs


def get_flavor_details(app, req, flavor_ref, detail=False):
    # extract details by decoding the id string
    flavor = {
        'id': flavor_ref['id'],
        'links': [
            {
                'href': app.get_endpoint_url('compute', req, 'v2_flavor',
                                             flavor_id=flavor_ref['id']),
                'rel': 'self',
            }
        ],

    }
    idstr = decode_fromb64_string(flavor_ref['id'])
    #id is delimited by :
    s = idstr.split(":")
    cpu= int(re.match(r'\d+', s[0]).group())
    ram = int(re.match(r'\d+', s[1]).group())*1024
    disk = int(re.match(r'\d+', s[2]).group())
    disk_type = s[3]
    names = "%d vCPU, %dGB ram, %dGB, %s" % (cpu, ram, disk, disk_type)
    flavor['name'] = names
    if detail:
        flavor['disk'] = disk
        flavor['ram'] = ram
        flavor['vcpus'] = cpu
        flavor['OS-FLV-DISK-TYPE:disk_type'] = disk_type
        flavor['swap'] = ''
        flavor['rxtx_factor'] = 1
        flavor['os-flavor-access:is_public'] = True
        flavor['OS-FLV-EXT-DATA:ephemeral'] = 0
        flavor['OS-FLV-DISABLED:disabled'] = False

    return flavor


def get_flavor_details_old(app, req, flavor_ref, detail=False):
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
        flavor['OS-FLV-DISK-TYPE:disk_type']= flavor_ref['disk-type']
        flavor['swap'] = ''
        flavor['rxtx_factor'] = 1
        flavor['os-flavor-access:is_public'] = True
        flavor['OS-FLV-EXT-DATA:ephemeral'] = 0
        flavor['OS-FLV-DISABLED:disabled'] = False

    return flavor

