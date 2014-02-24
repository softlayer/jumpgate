from functools import wraps
import inspect


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
    @wraps(handler)
    def wrapped(ex, req, resp, params):
        handler(ex, req, resp, params)
        for hook in after:
            hook(req, resp)

    propagate_argspec(wrapped, handler)

    return wrapped
