

def add_endpoints(disp):
    # V2 API - http://developer.openstack.org/api-ref-networking-v2.html

    disp.add_endpoint('v2_network', '/v2.0/networks/{network_id}')
    disp.add_endpoint('v2_networks', '/v2.0/networks')
    disp.add_endpoint('v2_subnet', '/v2.0/subnets/{subnet_id}')
    disp.add_endpoint('v2_subnets', '/v2.0/subnets')
    disp.add_endpoint('v2_extensions', '/v2.0/extensions')
