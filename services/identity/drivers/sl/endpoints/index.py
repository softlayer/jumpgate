import json
import falcon

from services.common.utils import get_url


class SLIdentityIndex(object):
    def on_get(self, req, resp):
        versions = {
            'id': 'v2.0',
            'links': [
                {'href': get_url('index'), 'rel': 'self'},
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
