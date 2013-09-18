from services.common.dispatcher import Dispatcher
from core import api

storage_dispatcher = Dispatcher(api)

# V2 API - http://api.openstack.org/api-ref.html#volumes-api

storage_dispatcher.add_endpoint('v2_volumes', '/v2/{tenant_id}/volumes')
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
