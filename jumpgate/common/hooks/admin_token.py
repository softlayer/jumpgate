import logging

from oslo.config import cfg

from jumpgate.common import hooks


cfg.CONF.register_opts([cfg.StrOpt('admin_token',
                                   secret=True,
                                   default='ADMIN')],
                       group='DEFAULT')
LOG = logging.getLogger(__name__)


@hooks.request_hook(True)
def admin_token(req, resp, kwargs):
    auth_token = req.headers.get('X-AUTH-TOKEN', None)
    admin_token = cfg.CONF['DEFAULT']['admin_token']

    if (admin_token is not None and auth_token is not None
            and admin_token == auth_token):
        # admin_token authenticates to Jumpgate API, but does not
        # provide SLAPI access
        req.env['is_admin'] = True
        LOG.debug("Admin access permitted")
