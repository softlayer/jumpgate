from jumpgate.common.error_handling import not_implemented
import logging
logger = logging.getLogger(__name__)


class NYI(object):

    def _standard_responder(self, req, resp):
        logger.warning("UNKNOWN PATH: %s %s", req.method, req.path)
        not_implemented(resp, 'Not Implemented', details='Not Implemented')

    on_get = _standard_responder
    on_post = _standard_responder
    on_put = _standard_responder
    on_delete = _standard_responder
    on_head = _standard_responder
    on_trace = _standard_responder
    on_patch = _standard_responder
    on_connect = _standard_responder
    on_options = _standard_responder
