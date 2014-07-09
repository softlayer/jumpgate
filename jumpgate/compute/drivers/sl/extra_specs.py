import mock

from jumpgate.common import error_handling
from jumpgate.compute.drivers.sl import flavor_list_loader


class ExtraSpecsFlavorV2(object):
    def __init__(self, app):
        self.app = app

    def on_get(self, req, resp, tenant_id, flavor_id):
        '''Returns the extra specs for a particular flavor

        '''
        all_flavors = flavor_list_loader.Flavors.get_flavors(mock.MagicMock())
        for flavor in all_flavors:
            if str(flavor_id) == flavor['id']:
                extra_specs = flavor['extra_specs']
                resp.status = 200
                resp.body = {'extra_specs': extra_specs}
                return
            else:
                error_handling.bad_request(resp, message="Invalid Flavor ID "
                                           "requested.")
        return


class ExtraSpecsFlavorKeyV2(object):
    def __init__(self, app):
        self.app = app

    def on_get(self, req, resp, tenant_id, flavor_id, key_id):
        '''Returns the requested key from the optional extra specs

        '''
        all_flavors = flavor_list_loader.Flavors.get_flavors(mock.MagicMock())
        for flavor in all_flavors:
            if str(flavor_id) == flavor['id']:
                extra_specs = flavor['extra_specs']
                if key_id in extra_specs:
                    resp.status = 200
                    resp.body = {key_id: extra_specs[key_id]}
                    return
                else:
                    error_handling.bad_request(resp, message="Invalid Key ID "
                                               "requested")
                    return
            else:
                error_handling.bad_request(resp, message="Invalid Flavor ID "
                                           "requested.")
                return
