import requests

from oslo.config import cfg

opts = [
    cfg.StrOpt('baremetal_endpoint', default='http://127.0.0.1:6385'),
    cfg.StrOpt('compute_endpoint', default='http://127.0.0.1:8774'),
    cfg.StrOpt('identity_endpoint', default='http://127.0.0.1:5000'),
    cfg.StrOpt('image_endpoint', default='http://127.0.0.1:9292'),
    cfg.StrOpt('network_endpoint', default='http://127.0.0.1:9696'),
    cfg.StrOpt('volume_endpoint', default='http://127.0.0.1:8776'),
]

cfg.CONF.register_opts(opts, group='openstack')


def setup_responder(app, disp, service):
    responder = OpenStackResponder(disp.mount, service)

    for endpoint in disp.get_unused_endpoints():
        disp.set_handler(endpoint, responder)


class OpenStackResponder(object):
    def __init__(self, mount, service):
        self.mount = mount
        self.service = service
        endpoint = cfg.CONF['openstack'][service + '_endpoint']
        self.endpoint = endpoint.rstrip('/')

    def _standard_responder(self, req, resp, **kwargs):
        data = None
        if req.method == 'POST' or req.method == 'PUT':
            data = req.stream.read()

        relative_uri = req.relative_uri
        if self.mount:
            relative_uri = relative_uri.replace(self.mount, '', 1)
        endpoint = self.endpoint + relative_uri

        os_resp = requests.request(req.method,
                                   endpoint,
                                   data=data,
                                   headers=req.headers,
                                   stream=True)

        resp.status = os_resp.status_code
        content_type = os_resp.headers.pop(
            'Content-Type', 'application/json').split(';', 1)[0]

        # Hack for test_delete_image_blank_id test. Somehow text/html comes
        # back as the content-type when it's supposed to be text/plain.
        if content_type == 'text/html':
            content_type = 'text/plain; charset=UTF-8'
        resp.content_type = content_type
        resp.stream_len = os_resp.headers.pop('Content-Length')
        resp.set_headers(os_resp.headers)
        resp.stream = os_resp.raw

    on_get = _standard_responder
    on_post = _standard_responder
    on_put = _standard_responder
    on_delete = _standard_responder
    on_head = _standard_responder
    on_trace = _standard_responder
    on_patch = _standard_responder
    on_connect = _standard_responder
    on_options = _standard_responder
