import time
import json
import base64

from SoftLayer import (
    Client, SoftLayerAPIError, TokenAuthentication, BasicAuthentication)

from jumpgate.common.aes import decode_aes
from jumpgate.common.utils import lookup
from jumpgate.common.exceptions import Unauthorized

USER_MASK = 'id, username, accountId'


def get_token_details(token, tenant_id=None):
    try:
        token_details = json.loads(decode_aes(base64.b64decode(token)))
    except (TypeError, ValueError):
        raise Unauthorized('Invalid Key')

    if time.time() > token_details['expires']:
        raise Unauthorized('Expired Key')

    if tenant_id and str(token_details['tenant_id']) != tenant_id:
        raise Unauthorized('Tenant/token Mismatch')

    return token_details


def get_new_token(credentials):
    username = lookup(credentials, 'auth', 'passwordCredentials', 'username')
    credential = lookup(credentials, 'auth', 'passwordCredentials', 'password')
    
    def assert_tenant(user):
        tenant = lookup(credentials, 'auth', 'tenantId')
        if tenant and str(user['accountId']) != tenant:
            raise Unauthorized('Invalid username, password or tenant id')

    # If the 'password' is the right length, treat it as an API api_key
    if len(credential) == 64:
        client = Client(username=username, api_key=credential)
        user = client['Account'].getCurrentUser(mask=USER_MASK)
        assert_tenant(user)
        return {'username': username,
                'api_key': credential,
                'auth_type': 'api_key',
                'tenant_id': str(user['accountId']),
                'expires': time.time() + (60 * 60 * 24)}, user
    else:
        client = Client()
        client.auth = None
        try:
            userId, tokenHash = client.authenticate_with_password(username,
                                                                  credential)
            user = client['Account'].getCurrentUser(mask=USER_MASK)
            assert_tenant(user)
            return {'userId': userId,
                    'tokenHash': tokenHash,
                    'auth_type': 'token',
                    'tenant_id': str(user['accountId']),
                    'expires': time.time() + (60 * 60 * 24)}, user
        except SoftLayerAPIError as e:
            if e.faultCode == 'SoftLayer_Exception_User_Customer_LoginFailed':
                raise Unauthorized(e.faultString)
            raise
        
def get_new_token_v3(credentials):
    
    credential = lookup(credentials, 'auth', 'identity', 'password','user','password')
    username = lookup(credentials, 'auth', 'identity','password','user','name')
    
    def assert_tenant(user):
        tenant = lookup(credentials, 'auth', 'tenantId')
        if tenant and str(user['accountId']) != tenant:
            raise Unauthorized('Invalid username, password or tenant id')

    

    # If the 'password' is the right length, treat it as an API api_key
    if len(credential) == 64:
        client = Client(username=username, api_key=credential)
        user = client['Account'].getCurrentUser(mask=USER_MASK)
        assert_tenant(user)
        return {'username': username,
                'api_key': credential,
                'auth_type': 'api_key',
                'tenant_id': str(user['accountId']),
                'expires': time.time() + (60 * 60 * 24)}, user
    else:
        client = Client()
        client.auth = None
        try:
            userId, tokenHash = client.authenticate_with_password(username,
                                                                  credential)
            user = client['Account'].getCurrentUser(mask=USER_MASK)
            assert_tenant(user)
            return {'userId': userId,
                    'tokenHash': tokenHash,
                    'auth_type': 'token',
                    'tenant_id': str(user['accountId']),
                    'expires': time.time() + (60 * 60 * 24)}, user
        except SoftLayerAPIError as e:
            if e.faultCode == 'SoftLayer_Exception_User_Customer_LoginFailed':
                raise Unauthorized(e.faultString)
            raise        


def get_auth(token_details):
    if token_details['auth_type'] == 'api_key':
        return BasicAuthentication(token_details['username'],
                                   token_details['api_key'])
    elif token_details['auth_type'] == 'token':
        return TokenAuthentication(token_details['userId'],
                                   token_details['tokenHash'])

    return None
