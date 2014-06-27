import json
import uuid

from falcon import status_codes

from jumpgate.common import hooks


@hooks.response_hook(False)
def hook_format(req, resp):
    body = resp.body
    if body is not None and not resp.content_type:
        resp.content_type = 'application/json'
        resp.body = json.dumps(body)

    if isinstance(resp.status, int):
        resp.status = getattr(status_codes,
                              'HTTP_%s' % resp.status,
                              resp.status)

    resp.set_header('X-Compute-Request-Id', req.env['REQUEST_ID'])


@hooks.request_hook(False)
def hook_set_uuid(req, resp, kwargs):
    req.env['REQUEST_ID'] = 'req-' + str(uuid.uuid1())
