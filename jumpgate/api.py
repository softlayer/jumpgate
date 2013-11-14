import configparser
import importlib
import uuid

from falcon import API

from jumpgate.common.nyi import NYI
from jumpgate.common.format import format_hook


class Jumpgate(API):
    """ Class docs go here. """

    before_hooks = []
    after_hooks = []

    config = {
        'installed_modules': {},
    }


def before_request(req, resp, kwargs):
    req.env['REQUEST_ID'] = str(uuid.uuid1())
    for hook in Jumpgate.before_hooks:
        hook(req, resp, kwargs)


def after_request(req, resp):
    for hook in Jumpgate.after_hooks:
        hook(req, resp)

    format_hook(req, resp)

    print(req.method,
          req.path,
          req.query_string,
          resp.status,
          '[ReqId: %s]' % req.env['REQUEST_ID'])


def make_app():
    # The core application of the translation layer
    api = Jumpgate(before=[before_request],
                   after=[after_request])

    # An easy class that can be used to implement endpoints that are
    # Not Yet Implemented.
    nyi = NYI()

    # Set the default route to the NYI object
    api.set_default_route(nyi)
    return api


def load_modules(api):
    # Load the config file to determine which modules are available
    config = configparser.ConfigParser()
    config.read('jumpgate.conf')

    # If there is a driver config file, we should read that too.
    driver_config = configparser.ConfigParser()
    driver_config.read('driver.conf')
    api.config['driver_config'] = driver_config

    for service in ['openstack', 'shared', 'identity', 'compute', 'image',
                    'block_storage', 'network', 'baremetal']:
        if service in config:
            importlib.import_module(config[service].get('driver'))
            api.config['installed_modules'][service] = True
        else:
            api.config['installed_modules'][service] = False

app = make_app()
# Modules need a reference to the global app instance.
load_modules(app)
