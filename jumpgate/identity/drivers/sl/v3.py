class V3(object):

    def __init__(self, disp):
        self.disp = disp

    def on_get(self, req, resp):
        resp.body = {"version": {
            "status": "stable",
            "updated": "2013-03-06T00:00:00Z",
            "media-types": [{
                "base": "application/json",
                "type": "application/vnd.openstack.identity-v3+json"
                }],
            "id": "v3.0",
            "links": [{
                "href": self.disp.get_endpoint_url(req, 'v3_auth_index'),
                "rel": "self"
                }]
            }
        }
