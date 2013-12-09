

def add_endpoints(disp):
    # V2 API - http://docs.openstack.org/developer/ironic/dev/api-spec-v1.html

    disp.add_endpoint('v1_versions', '/v1/versions')
    disp.add_endpoint('v1_version', '/v1/versions/{version_id}')

    disp.add_endpoint('v1_nodes', '/v1/nodes')
    disp.add_endpoint('v1_node', '/v1/nodes/{node_id}')
    disp.add_endpoint('v1_nodes_detail', '/v1/nodes/detail')

    disp.add_endpoint('v1_chassis', '/v1/chassis')
    disp.add_endpoint('v1_chassis_single', '/v1/chassis/{chassis_id}}')
    disp.add_endpoint('v1_chassis_detail', '/v1/chassis/detail')

    disp.add_endpoint('v1_ports', '/v1/ports')
    disp.add_endpoint('v1_port', '/v1/ports/{port_id}')
    disp.add_endpoint('v1_ports_detail', '/v1/ports/detail')

    disp.add_endpoint('v1_drivers', '/v1/drivers')
    disp.add_endpoint('v1_driver', '/v1/drivers/{driver_id}')

    disp.add_endpoint('v1_images', '/v1/images')
    disp.add_endpoint('v1_image', '/v1/images/{image_id}')

    disp.add_endpoint('v1_driver_configuration',
                      '/v1/nodes/{node_id}/driver_configuration')
    disp.add_endpoint('v1_driver_configuration_parameters',
                      '/v1/nodes/{node_id}/driver_configuration/parameters')

    disp.add_endpoint('v1_state', '/v1/nodes/{node_id}/state')

    disp.add_endpoint('v1_meta_data', '/v1/nodes/{node_id}/meta_data')

    disp.add_endpoint('v1_vendor_passthru',
                      '/v1/nodes/{node_id}/vendor_passthru/{method_name}')
