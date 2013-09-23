import json
import falcon

from services.compute import compute_dispatcher as disp


class SLComputeV2Flavor(object):
    def on_get(self, req, resp, flavor_id, tenant_id=None):
        flavor = {
            'disk': 25,
            'id': '1',
            'links': [
                {
                    'href': disp.get_endpoint_url('v2_flavor',
                                                  flavor_id=flavor_id),
                    'rel': 'self',
                }
            ],
            'name': 'custom',
            'ram': 1024,
            'vcpus': 2,
        }

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'flavor': flavor})


class SLComputeV2Flavors(object):
    def on_get(self, req, resp, tenant_id=None):
        flavor = {
            'disk': 25,
            'id': '1',
            'links': [
                {
                    'href': disp.get_endpoint_url('v2_flavor',
                                                  flavor_id='1'),
                    'rel': 'self',
                }
            ],
            'name': 'custom',
            'ram': 1024,
            'vcpus': 2,
            'swap': '',
            'rxtx_factor': 10,
            'os-flavor-access:is_public': True,
            'OS-FLV-EXT-DATA:ephemeral': 0,
            'OS-FLV-DISABLED:disabled': False,
        }

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'flavors': [flavor]})
