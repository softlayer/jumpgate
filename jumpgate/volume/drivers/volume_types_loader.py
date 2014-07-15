import json
import logging

LOG = logging.getLogger(__name__)

VOLUME_TYPE_1 = {
    "id": "241",
    "name": "san",
    "extra_specs": {
        "capabilities:volume_backend_name": "sjc01",
        "drivers:display_name": "default",
        "drivers:san_backed_disk": True,
        "drivers:exact_capacity": False
        }
}

VOLUME_TYPE_LIST = {"volume_types": [VOLUME_TYPE_1]}


class VolumeTypesLoader(object):

    def get_volume_types(self):
        return self._volume_types

    def __init__(self, json_str):
        try:
            json_format_error = False
            self.conf = VOLUME_TYPE_LIST
            self._volume_types = json.loads(json_str)
            if 'volume_types' not in self._volume_types:
                raise Exception('Unable to load "volume_types" from'
                                ' configuration file.')
            id_cache = set()
            for v_type in self._volume_types['volume_types']:
                self._validate_volume_type(v_type, id_cache)
        except (ValueError, TypeError):
            LOG.error('JSON FORMATTING ERROR in jumpgate.conf or config.py!')
            json_format_error = True
            pass
        except LookupError as e:
            LOG.error(str(e))
            pass
        except Exception as e:
            LOG.error(str(e))
            pass
        # LEAVE EMPTY LIST IF JSON ERROR!!!!!!!!
        if json_format_error:
            self._volume_types = {'volume_types': []}
        elif not self._volume_types or (
                'volume_types' not in self._volume_types):
            self._volume_types = self.conf

    def _validate_volume_type(self, v_type, id_cache):
        delete = False
        errors = []
        exspecs = self.conf['volume_types'][0]['extra_specs']
        vbn = exspecs['capabilities:volume_backend_name']
        dn = exspecs['drivers:display_name']
        sbd = exspecs['drivers:san_backed_disk']
        ec = exspecs['drivers:exact_capacity']
        if 'id' not in v_type:
            delete = True
            LOG.error('Expects volume_types with "id" key.')
        if 'name' not in v_type:
            delete = True
            LOG.error('Expects volume_types with "name" key.')
        if 'extra_specs' not in v_type:
            v_type['extra_specs'] = exspecs
            raise LookupError('Expects volume_types with "extra_specs" key.'
                              '  Replaced with default values.')
        if 'capabilities:volume_backend_name' not in v_type['extra_specs']:
            v_type['extra_specs']['capabilities:volume_backend_name'] = vbn
            errors.append('capabilities:volume_backend_name')
        if 'drivers:display_name' not in v_type['extra_specs']:
            v_type['extra_specs']['drivers:display_name'] = dn
            errors.append('drivers:display_name')
        if 'drivers:san_backed_disk' not in v_type['extra_specs']:
            v_type['extra_specs']['drivers:san_backed_disk'] = sbd
            errors.append('drivers:san_backed_disk')
        if 'drivers:exact_capacity' not in v_type['extra_specs']:
            v_type['extra_specs']['drivers:exact_capacity'] = ec
            errors.append('drivers:exact_capacity')
        if not isinstance(v_type['extra_specs']['drivers:exact_capacity'],
                          bool):
            raise Exception('Expects type of'
                            ' drivers:exact_capacity to be bool')
        if not isinstance(v_type['extra_specs']['drivers:san_backed_disk'],
                          bool):
            raise Exception('Expects type of'
                            ' drivers:san_backed_disk to be bool')

        if errors:
            LOG.error('Replaced ' + ", ".join(errors) +
                      ' with default values')
        if delete:
            self._volume_types['volume_types'].remove(v_type)

        # id field present, check for duplicates
        if 'id' in v_type:
            if v_type['id'] not in id_cache:
                id_cache.add(v_type['id'])
            else:
                self._volume_types['volume_types'].remove(v_type)
                LOG.error('Duplicate detected and deleted')
