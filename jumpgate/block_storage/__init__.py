from jumpgate.common.dispatcher import Dispatcher
from jumpgate.api import app

storage_dispatcher = Dispatcher(app)

# V2 API - http://api.openstack.org/api-ref-blockstorage.html#volumes-api

storage_dispatcher.add_endpoint('v2_volumes', '/v2/{tenant_id}/volumes')
storage_dispatcher.add_endpoint('v2_os_volumes', '/v2/{tenant_id}/os-volumes')

storage_dispatcher.add_endpoint('v2_volumes_detail',
                                '/v2/{tenant_id}/volumes/detail')
storage_dispatcher.add_endpoint('v2_volume',
                                '/v2/{tenant_id}/volumes/{volume_id}')
storage_dispatcher.add_endpoint('v2_volume_types', '/v2/{tenant_id}/types')
storage_dispatcher.add_endpoint('v2_volume_type',
                                '/v2/{tenant_id}/types/{type_id}')
storage_dispatcher.add_endpoint('v2_snapshots', '/v2/{tenant_id}/snapshots')
storage_dispatcher.add_endpoint('v2_snapshot',
                                '/v2/{tenant_id}/snapshots/{snapshot_id}')

# V1 API - Unknown link

storage_dispatcher.add_endpoint('v1_snapshots_detail',
                                '/v1/{tenant_id}/snapshots/detail')
storage_dispatcher.add_endpoint('v1_volume_types', '/v1/{tenant_id}/types')
storage_dispatcher.add_endpoint('v1_volumes_detail',
                                '/v1/{tenant_id}/volumes/detail')
storage_dispatcher.add_endpoint('v1_volume',
                                '/v1/{tenant_id}/volumes/{volume_id}')
