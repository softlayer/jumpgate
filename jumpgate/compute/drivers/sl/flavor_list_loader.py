import json
import logging
import os

LOG = logging.getLogger(__name__)

flavor1 = {"disk-type": "SAN", "name": "1 vCPU, 1GB ram, 25GB, SAN",
           "ram": 1024, "cpus": 1, "disk": 25, "id": "1", "portspeed": 100}
flavor2 = {"disk-type": "SAN", "name": "1 vCPU, 1GB ram, 100GB, SAN",
           "ram": 1024, "cpus": 1, "disk": 100, "id": "2", "portspeed": 100}
flavor3 = {"disk-type": "SAN", "name": "2 vCPU, 2GB ram, 100GB, SAN",
           "ram": 2048, "cpus": 2, "disk": 100, "id": "3", "portspeed": 100}
flavor4 = {"disk-type": "SAN", "name": "4 vCPU, 4GB ram, 100GB, SAN",
           "ram": 4096, "cpus": 4, "disk": 100, "id": "4", "portspeed": 100}
flavor5 = {"disk-type": "SAN", "name": "8 vCPU, 8GB ram, 100GB, SAN",
           "ram": 8192, "cpus": 8, "disk": 100, "id": "5", "portspeed": 100}
FLAVOR_DICT = {'1': flavor1, '2': flavor2, '3': flavor3, '4': flavor4,
               '5': flavor5}


class Flavors(object):
    _flavors = None

    @classmethod
    def get_flavors(cls, app):
        try:
            if cls._flavors is None:
                json_file = app.config.flavors.flavor_list
                if not os.path.exists(json_file):
                    json_file = app.config.find_file(json_file)

                if json_file is None:
                    raise ValueError('flavor_list.json not found')

                with open(json_file) as jf:
                    json_str = jf.read()
                    flavors = json.loads(json_str)
                    cls._flavors = {
                        int(key): format_flavor_extra_specs(val)
                        for key, val in flavors.items()
                    }
        except Exception as err_str:
            LOG.info(str(err_str))
            cls._flavors = {int(key): format_flavor_extra_specs(val)
                            for key, val in FLAVOR_DICT.items()}
        # Set flavor '1' as the default
        cls._flavors[None] = cls._flavors[1]
        return get_listing_flavors(cls._flavors)


def format_flavor_extra_specs(flavor):
    '''Formats the extra specs of a flavor into a 'extra_specs' key

    '''
    default_specs = {'disk': '', 'cpus': '', 'links': '', 'name': '',
                     'ram': '', 'id': '', 'OS-FLV-DISABLED:disabled': '',
                     'OS-FLV-EXT-DATA:ephemeral': '', 'rxtx_factor': '',
                     'disk-type': '', 'swap': '',
                     'os-flavor-access:is_public': ''}
    # Delete required parameters from response
    diff_specs = list(set(flavor.keys()).difference(set(default_specs.keys())))
    extra_specs = {}
    for key in diff_specs:
        extra_specs[key] = flavor[key]
        del flavor[key]
    flavor['extra_specs'] = extra_specs
    return flavor


def is_valid_flavor(flavor, id_set):
    '''Checks whether all the parameters of the flavor are correctly set

    '''
    if 'name' not in flavor:
        return False
    elif 'id' not in flavor:
        return False
    elif 'disk' not in flavor or type(flavor['disk']) != int:
        return False
    elif 'ram' not in flavor or type(flavor['ram']) != int:
        return False
    elif 'cpus' not in flavor or type(flavor['cpus']) != int:
        return False
    elif int(flavor['id']) in id_set:
        return False
    return True


def get_listing_flavors(flavors_from_config):
    proper_flavors = []
    id_set = set()
    # Ignore all invalid or repeated flavors
    for flavor_id, flavor in flavors_from_config.items():
        if flavor_id and is_valid_flavor(flavor, id_set):
            proper_flavors.append(flavor)
            id_set.add(int(flavor['id']))
    return proper_flavors
