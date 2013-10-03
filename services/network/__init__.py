from services.common.dispatcher import Dispatcher
from core import api

network_dispatcher = Dispatcher(api)

# V2 API - http://api.openstack.org/api-ref-networking.html

network_dispatcher.add_endpoint('v2_networks', '/v2.0/networks.json')
network_dispatcher.add_endpoint('v2_subnets', '/v2.0/subnets.json')
network_dispatcher.add_endpoint('v2_subnet', '/v2.0/subnets/{subnet_id}')
