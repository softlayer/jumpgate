import logging
import os
import os.path

from oslo.config import cfg

from jumpgate import api
from jumpgate import config as jumpgate_config

PROJECT = 'jumpgate'


def make_api(config_path=None):
    # Find configuration files
    config_files = cfg.find_config_files(PROJECT)

    # Check for environmental variable config file
    env_config_loc = os.environ.get('JUMPGATE_CONFIG')
    if env_config_loc and os.path.exists(env_config_loc):
        config_files.insert(0, env_config_loc)

    # Check for explit config file
    if config_path and os.path.exists(config_path):
        config_files.insert(0, config_path)

    if not config_files:
        raise Exception('No config files for %s found.' % PROJECT)

    jumpgate_config.CONF(project=PROJECT,
                         args=[],  # We don't want CLI arguments
                         default_config_files=config_files)

    logger = logging.getLogger(PROJECT)
    logger.setLevel(getattr(logging,
                            jumpgate_config.CONF['log_level'].upper()))
    logger.addHandler(logging.StreamHandler())
    app = api.Jumpgate()
    app.load_endpoints()
    app.load_drivers()

    return app.make_api()
