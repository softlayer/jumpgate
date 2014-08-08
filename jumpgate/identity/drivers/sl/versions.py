import falcon


class Versions(object):
    def __init__(self, disp):
        self.disp = disp

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_300
        resp.body = {
            'versions': {
                'values': [
                    {
                        'id': 'v3.0',
                        'links': [
                            {
                                'href': self.disp.get_endpoint_url(
                                    req, 'v3_auth_index'),
                                'rel': 'self'
                            },
                            {
                                'href': 'http://docs.openstack.org/api/'
                                        'openstack-identity-service/3/'
                                        'content/',
                                'rel': 'describedby',
                                'type': 'text/html'
                            },
                            {
                                'href': 'http://docs.openstack.org/api/'
                                        'openstack-identity-service/3/'
                                        'identity-api-ref-3.pdf',
                                'rel': 'describedby',
                                'type': 'application/pdf'
                            }
                        ],
                        'media-types': [
                            {
                                'base': 'application/json',
                                'type': 'application/'
                                        'vnd.openstack.identity-v3+json'
                            }
                        ],
                        'status': 'stable',
                        'updated': '2014-04-17T00:00:00Z'
                    },
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
