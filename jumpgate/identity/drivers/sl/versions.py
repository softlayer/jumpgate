

class Versions(object):
    def __init__(self, disp):
        self.disp = disp

    def on_get(self, req, resp):
        resp.body = {
            'versions': {
                'values': [
                    {
                        'id': 'v2.0',
                        'links': [
                            {
                                'href': self.disp.get_endpoint_url(
                                    req, 'v2_auth_index'),
                                'rel': 'self'
                            },
                            {
                                'href': 'http://docs.openstack.org/api/'
                                        'openstack-identity-service/2.0/'
                                        'content/',
                                'rel': 'describedby',
                                'type': 'text/html'
                            },
                            {
                                'href': 'http://docs.openstack.org/api/'
                                        'openstack-identity-service/2.0/'
                                        'identity-dev-guide-2.0.pdf',
                                'rel': 'describedby',
                                'type': 'application/pdf'
                            }
                        ],
                        'media-types': [
                            {
                                'base': 'application/json',
                                'type': 'application/'
                                        'vnd.openstack.identity-v2.0+json'
                            }
                        ],
                        'status': 'stable',
                        'updated': '2013-03-06T00:00:00Z'
                    }
                ]
            }
        }
