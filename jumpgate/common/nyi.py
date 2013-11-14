from jumpgate.common.error_handling import not_implemented
import logging
logger = logging.getLogger(__name__)


class NYI(object):
    def on_get(self, req, resp):
        self._standard_responder(req, resp)

    def on_post(self, req, resp):
        self._standard_responder(req, resp)

    def on_put(self, req, resp):
        self._standard_responder(req, resp)

    def on_delete(self, req, resp):
        self._standard_responder(req, resp)

    def on_head(self, req, resp):
        self._standard_responder(req, resp)

    def _standard_responder(self, req, resp):
        logger.warning("UNKNOWN PATH: %s %s", req.method, req.path)
        not_implemented(resp, 'Not Implemented', details='Not Implemented')
