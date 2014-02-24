from oslo.config import cfg


opts = [
    cfg.StrOpt('provider', default='SOFTLAYER'),
    cfg.StrOpt('project_id'),
#    cfg.StrOpt('catalog_template_file', default='identity.templates'),
]

cfg.CONF.register_opts(opts, group='libcloud')
#cfg.CONF.register_opts([cfg.StrOpt('admin_token', secret=True,
#                                   default='ADMIN')], group='DEFAULT')
