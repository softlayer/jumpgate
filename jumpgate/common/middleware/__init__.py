import importlib
import logging

from jumpgate.common.config import CONF

LOG = logging.getLogger(__name__)

_request_hooks = []
_response_hooks = []
_loaded = False


def request_hook(hook):
    """Decorator for request hook functions.
    Request hook functions should take 3 arguments:
    req - The incoming request object.
    resp - The response object.
    kwargs - Request arg params.
    """
    LOG.debug("Adding request hook '%s'" % (str(hook)))
    _request_hooks.append(hook)


def response_hook(hook):
    """Decorator for response hook functions.
    Response hook functions should take 2 arguments:
    req - The incoming request object.
    resp - The response object.
    """
    LOG.debug("Adding response hook '%s'" % (str(hook)))
    _response_hooks.append(hook)


def _load_module(module):
    try:
        importlib.import_module(module)
    except ImportError:
        raise ImportError("Failed to import middleware module '%s'. Verify it "
                          "exists in PYTHONPATH" % (module))


def load_middleware():
    global _loaded
    if not _loaded:
        for hook in CONF['request_hooks'] + CONF['response_hooks']:
            LOG.debug("Importing middleware module '%s'" % (hook))
            _load_module(hook)
    _loaded = True


def request_hooks():
    load_middleware()
    return _request_hooks


def response_hooks():
    load_middleware()
    return _response_hooks
