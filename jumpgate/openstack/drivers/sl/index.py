

class IndexV2(object):
    def __init__(self, app):
        self.app = app

    def on_get(self, req, resp):
        versions = [{
            'id': 'v2.0',
            'links': [{
                'href': self.app.get_endpoint_url('compute', req, 'v2_index'),
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
                'href': self.app.get_endpoint_url('compute', req, 'v1_index'),
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
