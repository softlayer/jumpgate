from jumpgate.common.dispatcher import Dispatcher
from jumpgate.api import app

openstack_dispatcher = Dispatcher(app)

openstack_dispatcher.add_endpoint('main_index', '/')

openstack_dispatcher.add_endpoint('v3_index', '/v3')
openstack_dispatcher.add_endpoint('v2_index', '/v2')
