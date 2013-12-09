

class SubnetsV2(object):
    def on_get(self, req, resp):
        # client = req.env['sl_client']
        resp.body = {'subnets': []}
