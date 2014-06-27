import functools
import importlib
import inspect
import logging

LOG = logging.getLogger(__name__)
_driver_cache = {}


def lookup(dic, key, *keys):
    if keys:
        return lookup(dic.get(key, {}), *keys)
    return dic.get(key)


def propagate_argspec(wrapper, responder):
    if hasattr(responder, 'wrapped_argspec'):
        wrapper.wrapped_argspec = responder.wrapped_argspec
    else:
        wrapper.wrapped_argspec = inspect.getargspec(responder)


def wrap_handler_with_hooks(handler, after):
    @functools.wraps(handler)
    def wrapped(ex, req, resp, params):
        handler(ex, req, resp, params)
        for hook in after:
            hook(req, resp)

    propagate_argspec(wrapped, handler)

    return wrapped


def import_class(canonical_name):
    segs = canonical_name.split('.')
    module_name, clazz = '.'.join(segs[0: len(segs) - 1]), segs[-1]
    module = importlib.import_module(module_name)
    class_ref = getattr(module, clazz, None)
    if class_ref is None:
        raise ImportError("%s is not defined in %s" % (clazz, module_name))
    return class_ref


def load_driver(canonical_name):
    global _driver_cache
    try:
        driver = _driver_cache.get(canonical_name)
        if driver is None:
            driver = import_class(canonical_name)
            LOG.debug("Loaded driver '%s'" % (canonical_name))
            _driver_cache[canonical_name] = driver
        return driver()
    except ImportError as e:
        LOG.error("Unable to load driver '%s'" % (canonical_name))
        raise e
