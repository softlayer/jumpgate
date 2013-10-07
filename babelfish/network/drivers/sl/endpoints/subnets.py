

class SLNetworkV2Subnets(object):
    def on_get(self, req, resp, format=None):
        # client = req.env['sl_client']
        resp.body = {'subnets': []}
