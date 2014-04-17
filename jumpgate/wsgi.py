import os.path
import os
import logging
from oslo.config import cfg

from jumpgate.api import Jumpgate
from jumpgate.config import CONF

PROJECT = 'jumpgate'


def make_api(config=None):
    # Find configuration files
    config_files = cfg.find_config_files(PROJECT)

    # Check for environmental variable config file
    env_config_loc = os.environ.get('JUMPGATE_CONFIG')
    if env_config_loc and os.path.exists(env_config_loc):
        config_files.insert(0, env_config_loc)

    # Check for explit config file
    if config and os.path.exists(config):
        config_files.insert(0, config)

    if not config_files:
        raise Exception('No config files for %s found.' % PROJECT)

    CONF(project=PROJECT,
         args=[],  # We don't want CLI arguments to pass through here
         default_config_files=config_files)

    logger = logging.getLogger(PROJECT)
    logger.setLevel(getattr(logging, CONF['log_level'].upper()))
    logger.addHandler(logging.StreamHandler())
    app = Jumpgate()
    app.load_endpoints()
    app.load_drivers()

    api = app.make_api()
    return api
