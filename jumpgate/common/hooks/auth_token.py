import logging
import re

from jumpgate.common import exceptions
from jumpgate.common import hooks
from jumpgate.identity.drivers import core as identity


LOG = logging.getLogger(__name__)
NOAUTH = [re.compile(e) for e in ['GET:/$', 'GET:\/v[\d]+[\/]?$',
                                  'GET:\/v[\d]+.[\d]+[\/]?$',
                                  'POST:\/v[\d]+\/auth/tokens$',
                                  'POST:\/v[\d]+.[\d]+\/tokens$',
                                  'GET:\/v[\d]+\/tokens/\w+$',
                                  'GET:\/v[\d]+.[\d]+\/tokens/\w+$']]


def protected(target):
    for expr in NOAUTH:
        if expr.match(target):
            return False
    return True


@hooks.request_hook(True)
def validate_token(req, resp, kwargs):
    tenant_id = req.env.get('tenant_id', None)
    token = req.headers.get('X-AUTH-TOKEN', None)

    if (req.env.get('REMOTE_USER', None) is not None or
            req.env.get('is_admin', False) or
            req.env.get('auth', None) is not None):
        # upstream authentication
        return

    if token is not None:
        if tenant_id is None:
            tenant_id = kwargs.get('tenant_id',
                                   req.headers.get('X-AUTH-PROJECT-ID'))
            req.env['tenant_id'] = tenant_id

        LOG.debug("Authenticating request token '%s'" % (token))
        identity.validate_token_id(token, tenant_id=tenant_id)
        req.env['auth'] = identity.token_id_driver().token_from_id(token)
    elif protected("%s:%s" % (req.method, req.path)):
        raise exceptions.Unauthorized('Authentication token required')
