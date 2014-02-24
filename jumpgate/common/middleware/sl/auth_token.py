import logging

from jumpgate.common.middleware import request_hook
from jumpgate.common.sl.auth import get_token_details


LOG = logging.getLogger(__name__)


@request_hook
def token_auth(req, resp, kwargs):
    tenant_id = req.env.get('tenant_id', None)
    auth_token = req.headers.get('X-AUTH-TOKEN', None)

    if (req.env.get('REMOTE_USER', None) is not None or
            req.env.get('is_admin', False)):
        # upstream authentication
        return

    if auth_token is not None:
        if tenant_id is None:
            tenant_id = kwargs.get('tenant_id',
                                   req.headers.get('X-AUTH-PROJECT-ID'))
            req.env['tenant_id'] = tenant_id

        LOG.debug('Authenticating request auth token')
        req.env['auth_token'] = get_token_details(auth_token,
                                                  tenant_id=tenant_id)
