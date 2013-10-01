import configparser
import importlib

from services.common.babelfish import Babelfish, before_request
from services.common.nyi import NYI


# The core application of the translation layer
api = Babelfish(before=before_request)

# An easy class that can be used to implement endpoints that are
# Not Yet Implemented.
nyi = NYI()

# Load the config file to determine which modules are available
config = configparser.ConfigParser()
config.read('babelfish.conf')

# If there is a driver config file, we should read that too.
driver_config = configparser.ConfigParser()
driver_config.read('driver.conf')
api.config['driver_config'] = driver_config

for service in ['shared', 'identity', 'compute', 'image', 'block_storage']:
    if service in config:
        try:
            api.config['installed_modules'][service] = True
            driver = importlib.import_module(config[service].get('driver'))
            # api.config[service + '_driver'] = driver
        except ImportError as e:
            # TODO - Add logging
            print("Exception with %s:" % service, e)
            api.config['installed_modules'][service] = False

# Set the default route to the NYI object
api.set_default_route(nyi)
