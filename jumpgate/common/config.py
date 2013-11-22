from oslo.config import cfg

FILE_OPTIONS = {
    None: [
        cfg.ListOpt('enabled_services', default=[
            'identity',
            'compute',
            'image',
            'block_storage',
            'network,'
            'baremetal',
        ]),
        cfg.StrOpt('some_test_value', default='jumpgate.identity.drivers.sl'),
    ],
    'identity': [
        cfg.StrOpt('driver', default='jumpgate.identity.drivers.sl'),
        cfg.StrOpt('mount', default=None),
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
