from babelfish.compute import compute_dispatcher


class IndexV2(object):
    def on_get(self, req, resp):
        versions = [{
            'id': 'v2.0',
            'links': [{
                'href': compute_dispatcher.get_endpoint_url(req, 'v2_index'),
                'rel': 'self'
            }],
            'status': 'CURRENT',
            'media-types': [
                {
                    'base': 'application/json',
                    'type': 'application/vnd.openstack.compute.v1.0+json',
                }
            ],
        }, {
            'id': 'v1.0',
            'links': [{
                'href': compute_dispatcher.get_endpoint_url(req, 'v1_index'),
                'rel': 'self'
            }],
            'status': 'ACTIVE',
            'media-types': [
                {
                    'base': 'application/json',
                    'type': 'application/vnd.openstack.compute.v1.0+json',
                }
            ],
        }]

        resp.body = {'versions': versions}
