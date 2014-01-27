from jumpgate.common.error_handling import not_implemented
from jumpgate.common.hooks import hook_set_uuid, hook_log_request, hook_format
import logging
logger = logging.getLogger(__name__)


class NYI(object):

    def __call__(self, req, resp, **kwargs):
        hook_set_uuid(req, resp, kwargs)
        logger.warning("UNKNOWN PATH: %s %s", req.method, req.path)
        not_implemented(resp, 'Not Implemented', details='Not Implemented')
        hook_format(req, resp)
        hook_log_request(req, resp)
