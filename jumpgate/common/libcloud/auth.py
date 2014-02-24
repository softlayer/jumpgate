from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

import time
from oslo.config import cfg

from jumpgate.common.utils import lookup
from jumpgate.config import CONF


def get_new_token(credentials):
    username = lookup(credentials, 'auth', 'passwordCredentials', 'username')
    credential = lookup(credentials, 'auth', 'passwordCredentials', 'password')

#    def assert_tenant(user):
#        tenant = lookup(credentials, 'auth', 'tenantId')
#        if tenant and str(user['accountId']) != tenant:
#            raise Unauthorized('Invalid username, password or tenant id')

    # If the 'password' is the right length, treat it as an API api_key
    driver = getattr(Provider, CONF.libcloud.provider)
    cls = get_driver(driver)

    # TODO - Make this dynamic based on confs
    client_args = {
        'project': CONF.libcloud.project_id,
    }

    client = cls(username, credential, **client_args)

    print dir(client)
    #        assert_tenant(user)
    return {'username': username,
            'api_key': credential,
            'auth_type': 'api_key',
            # TODO - How do I get this?
            'tenant_id': 'TBD',
#                'tenant_id': str(user['accountId']),
            'expires': time.time() + (60 * 60 * 24)}, user
