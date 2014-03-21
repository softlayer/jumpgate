from oslo.config import cfg
from SoftLayer import API_PUBLIC_ENDPOINT

FILE_OPTIONS = {
    None: [
        cfg.ListOpt('enabled_services', default=['identity',
                                                 'compute',
                                                 'image',
                                                 'block_storage',
                                                 'network,'
                                                 'baremetal']),
        cfg.StrOpt('log_level', default='INFO',
                   help='Log level to report. '
                        'Options: DEBUG, INFO, WARNING, ERROR, CRITICAL'),
        cfg.StrOpt('secret_key',
                   default='SET ME',
                   help='Secret key used to encrypt tokens'),
        cfg.ListOpt('request_hooks', default=[]),
        cfg.ListOpt('response_hooks', default=[])
    ],
    'softlayer': [
        cfg.StrOpt('endpoint', default=API_PUBLIC_ENDPOINT),
        cfg.StrOpt('proxy', default=None),
        cfg.StrOpt('catalog_template_file', default='identity.templates'),
    ],
    'identity': [
        cfg.StrOpt('driver', default='jumpgate.identity.drivers.sl'),
        cfg.StrOpt('mount', default=None),
        cfg.StrOpt('auth_driver', default='jumpgate.identity.'
                   'drivers.sl.tokens.SLAuthDriver'),
        cfg.StrOpt('token_driver', default='jumpgate.identity.drivers.core.'
                   'JumpgateTokenDriver'),
        cfg.StrOpt('token_id_driver', default='jumpgate.identity.drivers.core.'
                   'AESTokenIdDriver')
    ],
    'compute': [
        cfg.StrOpt('driver', default='jumpgate.compute.drivers.sl'),
        cfg.StrOpt('mount', default='/compute'),
    ],
    'image': [
        cfg.StrOpt('driver', default='jumpgate.image.drivers.sl'),
        cfg.StrOpt('mount', default='/image'),
    ],
    'block_storage': [
        cfg.StrOpt('driver', default='jumpgate.block_storage.drivers.sl'),
        cfg.StrOpt('mount', default='/block_store'),
    ],
    'network': [
        cfg.StrOpt('driver', default='jumpgate.network.drivers.sl'),
        cfg.StrOpt('mount', default='/network'),
    ],
    'baremetal': [
        cfg.StrOpt('driver', default='jumpgate.baremetal.drivers.sl'),
        cfg.StrOpt('mount', default='/baremetal'),
    ]}

CONF = cfg.CONF


def configure(conf=None):
    if not conf:
        conf = CONF

    for section in FILE_OPTIONS:
        conf.register_opts(FILE_OPTIONS[section], group=section)
