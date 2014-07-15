from jumpgate.common import error_handling


class ExtraSpecsFlavorV2(object):
    def __init__(self, app, flavors):
        self.app = app
        self.flavors = flavors

    def on_get(self, req, resp, tenant_id, flavor_id):
        '''Returns the extra specs for a particular flavor

        '''
        for flavor in self.flavors:
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
    def __init__(self, app, flavors):
        self.app = app
        self.flavors = flavors

    def on_get(self, req, resp, tenant_id, flavor_id, key_id):
        '''Returns the requested key from the optional extra specs

        '''
        for flavor in self.flavors:
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
