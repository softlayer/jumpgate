import json
import falcon
from services.identity import identity_dispatcher


class SLIdentityV2Index(object):
    def on_get(self, req, resp):
        versions = {
            'id': 'v2.0',
            'links': [
                {'href': identity_dispatcher.get_endpoint_url(req, 'v2_index'),
                 'rel': 'self'},
            ],
            'status': 'CURRENT',
            'media-types': [
                {
                    'base': 'application/json',
                    'type': 'application/vnd.openstack.compute.v1.0+json',
                }
            ]
        }

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'versions': versions})
