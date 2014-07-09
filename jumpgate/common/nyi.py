import logging

from jumpgate.common import error_handling

logger = logging.getLogger(__name__)


class NYI(object):

    def __init__(self, before=None, after=None):
        # simulate before and after hooks
        self.before = before or []
        self.after = after or []

    def __call__(self, req, resp, **kwargs):
        for hook in self.before:
            hook(req, resp, kwargs)
        logger.warning("UNKNOWN PATH: %s %s", req.method, req.path)
        error_handling.not_implemented(resp, 'Not Implemented',
                                       details='Not Implemented')
        for hook in self.after:
            hook(req, resp)
