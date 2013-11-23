import os.path
import os

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
    app = Jumpgate()
    app.load_endpoints()
    app.load_drivers()

    api = app.make_api()
    return api
