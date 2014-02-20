import time

DEFAULT_TOKEN_DURATION = 60 * 60 * 24


class AuthTokenDriver(object):

    def _build_api_token(self, user, api_key, tenant,
                     expires=DEFAULT_TOKEN_DURATION):
        return {'username': user,
                'api_key': api_key,
                'auth_type': 'api_key',
                'tenant_id': tenant,
                'expires': time.time() + expires}

    def _build_credential_token(self, user, token, tenant,
                                expires=DEFAULT_TOKEN_DURATION):
        return {'userId': user,
                'tokenHash': token,
                'auth_type': 'token',
                'tenant_id': tenant,
                'expires': time.time() + expires}

    def get_new_token(self, credentials):
        """Authenticates credentials against identity provider and
        returns a jumpgate compatible token upon successful authentication.
        
        :param credentials: A dict containing the authentication credentials
        in keystone auth body request format."""
        raise NotImplementedError()
