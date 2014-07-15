from oslo.config import cfg
import SoftLayer


VOLUME_TYPE_1 = ('{"id": "241", "name": "san", "extra_specs": {'
                 '"capabilities:volume_backend_name": "sjc01",'
                 ' "drivers:display_name": "default", '
                 '"drivers:san_backed_disk"'
                 ': true, "drivers:exact_capacity": false}}')
VOLUME_TYPE_LIST = ('{"volume_types": [' + VOLUME_TYPE_1 + ']}')


FILE_OPTIONS = {
    None: [
        cfg.ListOpt('enabled_services', default=['identity',
                                                 'compute',
                                                 'image',
                                                 'volume',
                                                 'network,'
                                                 'baremetal']),
        cfg.StrOpt('log_level',
                   default='INFO',
                   help=('Log level to report. '
                         'Options: DEBUG, INFO, WARNING, ERROR, CRITICAL')),
        cfg.StrOpt('secret_key',
                   default='SET ME',
                   help='Secret key used to encrypt tokens'),
        cfg.ListOpt('request_hooks', default=[]),
        cfg.ListOpt('response_hooks', default=[]),
        cfg.StrOpt('default_domain', default='jumpgate.com')
    ],
    'softlayer': [
        cfg.StrOpt('endpoint', default=SoftLayer.API_PUBLIC_ENDPOINT),
        cfg.StrOpt('proxy', default=None),
        cfg.StrOpt('catalog_template_file', default='identity.templates'),
        cfg.StrOpt('noauth_user', default=''),
        cfg.StrOpt('noauth_api_key', default=''),
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
        cfg.StrOpt('default_injected_file_content_bytes', default=10240),
        cfg.StrOpt('default_injected_file_path_bytes', default=255),
        cfg.StrOpt('default_cores', default=200),
        cfg.StrOpt('default_floating_ips', default=100),
        cfg.StrOpt('default_injected_files', default=5),
        cfg.StrOpt('default_instances', default=10),
        cfg.StrOpt('default_key_pairs', default=100),
        cfg.StrOpt('default_metadata_items', default=128),
        cfg.StrOpt('default_ram', default=512000),
        cfg.StrOpt('default_security_group_rules', default=20),
        cfg.StrOpt('default_security_groups', default=10),
        cfg.StrOpt('default_availability_zone', default=None),
    ],
    'image': [
        cfg.StrOpt('driver', default='jumpgate.image.drivers.sl'),
        cfg.StrOpt('mount', default='/image'),
    ],
    'volume': [
        cfg.StrOpt('driver', default='jumpgate.volume.drivers.sl'),
        cfg.StrOpt('mount', default='/volume'),
        cfg.StrOpt('default_availability_zone', default=None),
        cfg.StrOpt('volume_name_prefix', default='jumpgate-san-'),
        cfg.StrOpt('volume_types', default='volume_types.json'),
    ],
    'network': [
        cfg.StrOpt('driver', default='jumpgate.network.drivers.sl'),
        cfg.StrOpt('mount', default='/network'),
    ],
    'baremetal': [
        cfg.StrOpt('driver', default='jumpgate.baremetal.drivers.sl'),
        cfg.StrOpt('mount', default='/baremetal'),
    ],
    'flavors': [
        cfg.StrOpt('flavor_list', default=None),
    ]}

CONF = cfg.CONF


def configure(conf=None):
    if not conf:
        conf = CONF

    for section in FILE_OPTIONS:
        conf.register_opts(FILE_OPTIONS[section], group=section)
