import logging

from jumpgate.common import hooks

LOG = logging.getLogger(__name__)


@hooks.request_hook(True)
def log_request(req, resp, kwargs):
    LOG.info('REQ: %s %s %s %s [ReqId: %s]',
             req.method,
             req.path,
             req.query_string,
             kwargs,
             req.env['REQUEST_ID'])


@hooks.response_hook(True)
def log_response(req, resp):
    LOG.info('RESP: %s %s %s %s [ReqId: %s]',
             req.method,
             req.path,
             req.query_string,
             resp.status,
             req.env['REQUEST_ID'])
