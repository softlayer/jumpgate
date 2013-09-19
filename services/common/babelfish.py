from falcon import API

#after_hooks = []
before_hooks = []


# def after_request(req, resp, kwargs):
#     for hook in after_hooks:
#         hook(req, resp, kwargs)


def before_request(req, resp, kwargs):
    for hook in before_hooks:
        hook(req, resp, kwargs)


class Babelfish(API):
    """ Class docs go here. """

    config = {
        'installed_modules': {},
    }

    current_tenant_id = None
