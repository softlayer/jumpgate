import os.path
import os
import logging

from jumpgate.api import Jumpgate
from jumpgate.config import CONF


def make_api():
    config_files = None
    env_config_loc = os.environ.get('JUMPGATE_CONFIG')
    if env_config_loc and os.path.exists(env_config_loc):
        config_files = [env_config_loc]

    CONF(project='jumpgate',
         args=[],  # We don't want CLI arguments to pass through here
         default_config_files=config_files)

    logger = logging.getLogger('jumpgate')
    logger.setLevel(getattr(logging, CONF['log_level'].upper()))
    logger.addHandler(logging.StreamHandler())
    app = Jumpgate()
    app.load_endpoints()
    app.load_drivers()

    api = app.make_api()
    return api
