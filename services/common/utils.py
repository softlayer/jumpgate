def get_url(action, tenant_id=None, version='2'):
    # TODO - Make this work more dynamically
    url = 'http://localhost:5000/v' + version + '/'

    if tenant_id:
        url += str(tenant_id) + '/'

    url += action
    return url
