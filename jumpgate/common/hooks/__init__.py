import importlib
import logging

from jumpgate.common.config import CONF


LOG = logging.getLogger(__name__)

_req_hooks = {'optional': [], 'required': []}
_res_hooks = {'optional': [], 'required': []}
_loaded = False


def request_hook(optional=True):
    """Decorator for request hook functions.
    Request hook functions should take 3 arguments:
    req - The incoming request object.
    resp - The response object.
    kwargs - Request arg params.
    """
    def _hook(hook):
        LOG.debug("Adding request hook '%s'" % (str(hook)))
        cache = _req_hooks['optional'] if optional else _req_hooks['required']
        cache.append(hook)
        return hook
    return _hook


def response_hook(optional=True):
    """Decorator for response hook functions.
    Response hook functions should take 2 arguments:
    req - The incoming request object.
    resp - The response object.
    """
    def _hook(hook):
        LOG.debug("Adding response hook '%s'" % (str(hook)))
        cache = _res_hooks['optional'] if optional else _res_hooks['required']
        cache.append(hook)
        return hook
    return _hook


def _load_module(module):
    try:
        importlib.import_module(module)
    except ImportError:
        raise ImportError("Failed to import hook module '%s'. Verify it "
                          "exists in PYTHONPATH" % (module))


def load_hooks():
    global _loaded
    if not _loaded:
        for hook in (['jumpgate.common.hooks.core'] + CONF['request_hooks'] +
                     CONF['response_hooks']):
            LOG.debug("Importing hook module '%s'" % (hook))
            _load_module(hook)
    _loaded = True


def required_request_hooks():
    load_hooks()
    return _req_hooks['required']


def optional_request_hooks():
    load_hooks()
    return _req_hooks['optional']


def required_response_hooks():
    load_hooks()
    return _res_hooks['required']


def optional_response_hooks():
    load_hooks()
    return _res_hooks['optional']
