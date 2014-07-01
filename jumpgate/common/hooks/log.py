import logging

from jumpgate.common import hooks

LOG = logging.getLogger(__name__)


@hooks.response_hook(True)
def log_request(req, resp):
    LOG.info('%s %s %s %s [ReqId: %s]',
             req.method,
             req.path,
             req.query_string,
             resp.status,
             req.env['REQUEST_ID'])
