import json
import logging
import time

import jumpgate.common.aes as aes
from jumpgate.config import CONF
import jumpgate.common.exceptions as exceptions
import jumpgate.common.utils as utils


DEFAULT_TOKEN_DURATION = 60 * 60 * 24
LOG = logging.getLogger(__name__)


def auth_driver():
    return utils.load_driver(CONF['identity']['auth_driver'])


def token_driver():
    return utils.load_driver(CONF['identity']['token_driver'])


def token_id_driver():
    return utils.load_driver(CONF['identity']['token_id_driver'])


def validate_token_id(token_id, user_id=None, username=None, tenant_id=None):
    token = token_id_driver().token_from_id(token_id)
    token_driver().validate_token(token, user_id, username, tenant_id)


class TokenDriver(object):

    def create_token(self, creds, auth_response):
        raise NotImplementedError()

    def validate_token(self, token):
        raise NotImplementedError()

    def create_credentials(self, token):
        raise NotImplementedError()

    def validate_access(self, token, user_id=None,
                        username=None, tenant_id=None):
        raise NotImplementedError()

    def tenant_id(self, token):
        raise NotImplementedError()

    def expires(self, token):
        raise NotImplementedError()

    def username(self, token):
        raise NotImplementedError()

    def user_id(self, token):
        raise NotImplementedError()


class TokenIdDriver(object):

    def create_token_id(self, token):
        raise NotImplementedError()

    def token_from_id(self, token_id):
        raise NotImplementedError()


class AuthDriver(object):

    def authenticate(self, creds):
        raise NotImplementedError()


class JumpgateTokenDriver(TokenDriver):

    def __init__(self):
        super(JumpgateTokenDriver, self).__init__()

    def create_token(self, creds, auth_response,
                     duration=DEFAULT_TOKEN_DURATION):
        return {'user_id': str(auth_response['user']['id']),
                'username': str(auth_response['user']['username']),
                'api_key': str(auth_response['credential']),
                'auth_type': auth_response['auth_type'],
                'tenant_id': str(auth_response['user']['accountId']),
                'expires': time.time() + duration}

    def create_credentials(self, token):
        return {'auth': {
                'tenantId': token['tenant_id'],
                'passwordCredentials': {
                    'username': token['username'],
                    'password': token['api_key']}
                }
                }

    def validate_access(self, token, user_id=None,
                        username=None, tenant_id=None):
        self.validate_token(token, user_id, username, tenant_id)
        auth = auth_driver().authenticate(self.create_credentials(token))
        return auth['user']

    def tenant_id(self, token):
        return token['tenant_id']

    def expires(self, token):
        return token['expires']

    def username(self, token):
        return token['username']

    def user_id(self, token):
        return token['user_id']

    def validate_token(self, token, user_id=None, username=None,
                       tenant_id=None):
        if time.time() > token['expires']:
            raise exceptions.InvalidTokenError("Expired token")

        if user_id and str(token['user_id']) != user_id:
            raise exceptions.InvalidTokenError("Invalid user ID")

        if username and str(token['username']) != username:
            raise exceptions.InvalidTokenError("Invalid username")

        if tenant_id and str(token['tenant_id']) != tenant_id:
            raise exceptions.InvalidTokenError("Invalid tenant ID")


class AESTokenIdDriver(TokenIdDriver):

    def __init__(self):
        super(AESTokenIdDriver, self).__init__()

    def create_token_id(self, token):
        return aes.encode_aes(json.dumps(token))

    def token_from_id(self, token_id):
        try:
            return json.loads(aes.decode_aes(token_id))
        except (TypeError, ValueError):
            raise exceptions.InvalidTokenError('Malformed token')
