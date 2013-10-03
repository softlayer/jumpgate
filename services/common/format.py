import json


def format_hook(req, resp):
    body = resp.body
    if body is not None and not resp.content_type:
        resp.content_type = 'application/json'
        resp.body = json.dumps(body)
