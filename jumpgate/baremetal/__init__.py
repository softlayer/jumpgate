from jumpgate.common.dispatcher import Dispatcher
from jumpgate.api import app

dispatcher = Dispatcher(app)

# V2 API - http://docs.openstack.org/developer/ironic/dev/api-spec-v1.html

dispatcher.add_endpoint('v1_versions', '/v1/versions')
dispatcher.add_endpoint('v1_version', '/v1/versions/{version_id}')

dispatcher.add_endpoint('v1_nodes', '/v1/nodes')
dispatcher.add_endpoint('v1_node', '/v1/nodes/{node_id}')
dispatcher.add_endpoint('v1_nodes_detail', '/v1/nodes/detail')

# TODO: CHASSIS SPEC NOT WELL DEFINED??
dispatcher.add_endpoint('v1_chassis', '/v1/chassis')

dispatcher.add_endpoint('v1_ports', '/v1/ports')
dispatcher.add_endpoint('v1_port', '/v1/ports/{port_id}')
dispatcher.add_endpoint('v1_ports_detail', '/v1/ports/detail')

dispatcher.add_endpoint('v1_drivers', '/v1/drivers')
dispatcher.add_endpoint('v1_driver', '/v1/drivers/{driver_id}')

dispatcher.add_endpoint('v1_images', '/v1/images')
dispatcher.add_endpoint('v1_image', '/v1/images/{image_id}')

dispatcher.add_endpoint('v1_driver_configuration',
                        '/v1/nodes/{node_id}/driver_configuration')
dispatcher.add_endpoint('v1_driver_configuration_parameters',
                        '/v1/nodes/{node_id}/driver_configuration/parameters')

dispatcher.add_endpoint('v1_state', '/v1/nodes/{node_id}/state')

dispatcher.add_endpoint('v1_meta_data', '/v1/nodes/{node_id}/meta_data')

dispatcher.add_endpoint('v1_vendor_passthru',
                        '/v1/nodes/{node_id}/vendor_passthru/{method_name}')
