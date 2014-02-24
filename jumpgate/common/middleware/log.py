import logging

from jumpgate.common.middleware import response_hook

LOG = logging.getLogger(__name__)


@response_hook
def log_request(req, resp):
    LOG.info('%s %s %s %s [ReqId: %s]',
             req.method,
             req.path,
             req.query_string,
             resp.status,
             req.env['REQUEST_ID'])
