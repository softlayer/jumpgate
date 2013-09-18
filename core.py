import configparser
import importlib

from services.common.babelfish import Babelfish
from services.common.nyi import NYI

# TODO - TEMPORARY OPENSTACK MAPPER
from services.openstack_mapper import OSMapper

# The core application of the translation layer
api = Babelfish()

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

if 'identity' in config:
    try:
        api.config['installed_modules']['identity'] = True
        driver = importlib.import_module(config['identity'].get('driver'))
#        api.config['identity_driver'] = driver
    except ImportError as e:
        # TODO - Add logging
        print("EXCEPTION:", e)
        api.config['installed_modules']['identity'] = False

# Set the default route to the NYI object
api.set_default_route(nyi)

# TODO - TEMPORARY OPENSTACK MAPPER
#api.set_default_route(OSMapper())

# TODO - Do API stuff here
#print(api._routes)
