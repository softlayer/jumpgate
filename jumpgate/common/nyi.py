import logging

from jumpgate.common.error_handling import not_implemented

logger = logging.getLogger(__name__)


class NYI(object):

    def __init__(self, before=[], after=[]):
        # simulate before and after hooks
        self.before = before
        self.after = after

    def __call__(self, req, resp, **kwargs):
        for hook in self.before:
            hook(req, resp, kwargs)
        logger.warning("UNKNOWN PATH: %s %s", req.method, req.path)
        not_implemented(resp, 'Not Implemented', details='Not Implemented')
        for hook in self.after:
            hook(req, resp)
