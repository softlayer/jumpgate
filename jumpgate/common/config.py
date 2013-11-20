from oslo.config import cfg

FILE_OPTIONS = {
    'identity': [
        cfg.StrOpt('driver', default='jumpgate.identity.drivers.sl')
    ],
    'compute': [
        cfg.StrOpt('driver', default='jumpgate.compute.drivers.sl')
    ],
    'image': [
        cfg.StrOpt('driver', default='jumpgate.image.drivers.sl')
    ],
    'block_storage': [
        cfg.StrOpt('driver', default='jumpgate.block_storage.drivers.sl')
    ],
    'openstack': [
        cfg.StrOpt('driver', default='jumpgate.openstack.drivers.sl')
    ],
    'network': [
        cfg.StrOpt('driver', default='jumpgate.network.drivers.sl')
    ],
    'baremetal': [
        cfg.StrOpt('driver', default='jumpgate.baremetal.drivers.sl')
    ]}

CONF = cfg.CONF


def configure(conf=None):
    if not conf:
        conf = CONF

    for section in FILE_OPTIONS:
        conf.register_opts(FILE_OPTIONS[section], group=section)
