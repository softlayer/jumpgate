from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from jumpgate.config import CONF


cls = get_driver(Provider.CONF['libcloud.provider'])

driver = cls(CONF['libcloud.client_id'], CONF['libcloud.secret'],
             project=CONF['libcloud.project_id'])
