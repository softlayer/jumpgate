import base64
import json
import logging
import time

from jumpgate.common import aes
from jumpgate.common import exceptions
from jumpgate.common import utils
from jumpgate import config

DEFAULT_TOKEN_DURATION = 60 * 60 * 24
LOG = logging.getLogger(__name__)


def auth_driver():
    return utils.load_driver(config.CONF['identity']['auth_driver'])


def token_driver():
    return utils.load_driver(config.CONF['identity']['token_driver'])


def token_id_driver():
    return utils.load_driver(config.CONF['identity']['token_id_driver'])


def validate_token_id(token_id, user_id=None, username=None, tenant_id=None):
    token = token_id_driver().token_from_id(token_id)
    token_driver().validate_token(token, user_id, username, tenant_id)


class TokenDriver(object):
    """Encapsulates auth token creation, validation and access

    This exists to provide a pluggable means for auth tokens.
    """

    def create_token(self, creds, auth, duration=DEFAULT_TOKEN_DURATION):
        """Creates a new auth token for the given parameters.

        :param creds: The request body in dict form as passed to the API
        for identity validation and token creation.
        :param auth: The auth object as returned from the AuthDriver's
        authenticate method.
        :param duration: The duration of the token's expires attribute
        given as the number of seconds.
        """
        raise NotImplementedError()

    def validate_token(self, token, user_id=None,
                       username=None, tenant_id=None):
        """Assert the specified token is still valid

        :param token: Token to validate.
        :param user_id: If specified the user_id associated with the token.
        :param username: If specified the username associated with the token.
        :param tenant_id: If specified the tenant ID assocaited with the token.
        """
        raise NotImplementedError()

    def create_credentials(self, token):
        """Creates a well formed credential dict from the given token.

        The format of the response should mimic that expected in the
        credentials argument of create_token.

        :param token: The token to create credentials for.
        """
        raise NotImplementedError()

    def validate_access(self, token, user_id=None,
                        username=None, tenant_id=None):
        """Validate the specified token still has access.

        Failure to validate the given token should raise an exception in the
        method implementation.

        :param user_id: If specified the user ID to validate token access for.
        :param username: If specified the username to validate token
        access for.
        :param tenant_id: If specified the tenant ID to validate token
        access for.
        """
        raise NotImplementedError()

    def tenant_id(self, token):
        """Extract the tenant ID from the given token.

        :param token: The token to extract the tenant ID from.
        """
        raise NotImplementedError()

    def tenant_name(self, token):
        """Extract the tenant name from the given token.

        :param token: The token to extract the tenant name from.
        """
        raise NotImplementedError()

    def expires(self, token):
        """Extract the expires timestamp from the token in time.time() format.

        :param token: The token to extract expires timestamp from.
        """
        raise NotImplementedError()

    def username(self, token):
        """Extract the username from the said token.

        :param token: The token to extract the username from.
        """
        raise NotImplementedError()

    def credential(self, token):
        """Extract the credential from the said token.

        :param token: The token to extract the credential from.
        """
        raise NotImplementedError()

    def user_id(self, token):
        """Extract the user ID from the given token.

        :param token: The token to extract the user ID from.
        """
        raise NotImplementedError()

    def roles(self, token):
        """Extracts the role id/name pairs from the token.

        The response should be a dict object who's key:value
        pairs equate to the role_id:role_name for each role
        in the token. For example: {'0':'admin', '1':'user'}

        :param token: The token to extract roles from.
        """
        raise NotImplementedError()


class TokenIdDriver(object):
    """Encapsulates concrete logic encode/decode a raw token

    Sent/received over the wire herein called a token ID.
    """

    def create_token_id(self, token):
        """Encode the raw token into its token ID format.

        :param token: The raw token to encode.
        """
        raise NotImplementedError()

    def token_from_id(self, token_id):
        """Decode an encoded token into its raw format.

        :param token_id: The encoded token to decode.
        """
        raise NotImplementedError()


class AuthDriver(object):
    """Encapsulates logic to authenticate an identity request

    Validates a consumer's identity and grants the consumer eligibility for
    an authentication token.
    """

    def authenticate(self, creds):
        """Performs authentication

        Authenticate the said credentials against an identity provider.
        Upon successful authentication implementations should return an
        auth object which typically contains additional details about the
        authenticated user. The format of the response object is determined
        by the requirements of the current TokenDriver's create_token method.
        Failure to authenticate can either raise an Unauthorized exception
        directly or return None from this method.

        :param creds: The credentials in dict form as passed to the API
        in a request to authenticate and obtain a new token.
        """
        raise NotImplementedError()


class JumpgateTokenDriver(TokenDriver):
    """Default Jumpgate token driver

    acceptable for many implementations needing to transport standard token
    attributes.
    """

    def __init__(self):
        super(JumpgateTokenDriver, self).__init__()

    def create_token(self, creds, auth,
                     duration=DEFAULT_TOKEN_DURATION):
        return {'user_id': str(auth['user']['id']),
                'username': str(auth['user']['username']),
                'api_key': str(auth['credential']),
                'auth_type': auth['auth_type'],
                'tenant_id': str(auth['user']['accountId']),
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
        if auth is None:
            raise exceptions.InvalidTokenError("Token is no longer valid")

    def tenant_id(self, token):
        return token['tenant_id']

    def tenant_name(self, token):
        return token['tenant_id']

    def expires(self, token):
        return token['expires']

    def username(self, token):
        return token['username']

    def credential(self, token):
        return token['api_key']

    def user_id(self, token):
        return token['user_id']

    def roles(self, token):
        return {'1': 'user'}

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
    """Default Jumpgate token ID driver

    uses AES + base64 to encode and decode a raw token.
    """

    def __init__(self):
        super(AESTokenIdDriver, self).__init__()

    def create_token_id(self, token):
        return base64.b64encode(aes.encode_aes(json.dumps(token)))

    def token_from_id(self, token_id):
        try:
            return json.loads(aes.decode_aes(base64.b64decode(token_id)))
        except (TypeError, ValueError):
            raise exceptions.InvalidTokenError('Malformed token')
