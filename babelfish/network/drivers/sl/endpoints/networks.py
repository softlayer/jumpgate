

class SLNetworkV2Networks(object):
    def on_get(self, req, resp, format=None):
        networks = [
            {
                "status": "ACTIVE",
                "admin_state_up": True,
                "subnets": [],
                "name": "private",
                "id": "private",
            },
            {
                "status": "ACTIVE",
                "admin_state_up": True,
                "subnets": [],
                "name": "public",
                "id": "public",
            },
        ]
        resp.body = {'networks': networks}
