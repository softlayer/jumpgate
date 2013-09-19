import configparser
import importlib

from services.common.babelfish import Babelfish, before_request
from services.common.nyi import NYI

# TODO - TEMPORARY OPENSTACK MAPPER
from services.openstack_mapper import OSMapper

# The core application of the translation layer
api = Babelfish(before=before_request)

# An easy class that can be used to implement endpoints that are
# Not Yet Implemented.
nyi = NYI()

# Load the config file to determine which modules are available
config = configparser.ConfigParser()
config.read_file(open('babelfish.conf'))

# If there is a driver config file, we should read that too.
try:
    driver_config = configparser.ConfigParser()
    driver_config.read_file(open('driver.conf'))
    api.config['driver_config'] = driver_config
except FileNotFoundError as e:
    # TODO - Add logging
    print("EXCEPTION:", e)
    api.config['driver_config'] = None

for service in ['identity', 'compute', 'image', 'block_storage']:
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

# TODO - TEMPORARY OPENSTACK MAPPER
#api.set_default_route(OSMapper())

# TODO - Do API stuff here
for route in api._routes:
    if 'servers' in route[0].pattern:
        print((route[0].pattern), route[1], "\n")
