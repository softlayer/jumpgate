import json
from SoftLayer import (
    Client, SoftLayerAPIError, TokenAuthentication, BasicAuthentication)

from jumpgate.common.error_handling import unauthorized, compute_fault
from jumpgate.common.utils import lookup


def get_password_auth(req, body=None):
    headers = req.headers

    if 'x-auth-token' in headers:
        (userId, hash) = headers['x-auth-token'].split(':')
    elif body:
        body = json.loads(body)
        username = lookup(body, 'auth', 'passwordCredentials', 'username')
        password = lookup(body, 'auth', 'passwordCredentials', 'password')

        client = Client()
        (userId, hash) = client.authenticate_with_password(username, password)
    else:
        return None, None, None

    auth = TokenAuthentication(userId, hash)
    token = str(userId) + ':' + hash
    return auth, token, None


def get_api_key_auth(req, body=None):
    headers = req.headers

    if 'x-auth-token' in headers:
        username, api_key = headers['x-auth-token'].split(':')
    elif body:
        body = json.loads(body)
        username = lookup(body, 'auth', 'passwordCredentials', 'username')
        api_key = lookup(body, 'auth', 'passwordCredentials', 'password')
    else:
        return None, None, None

    if len(api_key) != 64:
        return None, None, None

    auth = BasicAuthentication(username, api_key)
    token = str(username) + ':' + api_key
    return auth, token, None


def try_auth(f, req, resp, *args, **kwargs):
    try:
        return f(req, *args, **kwargs)
    except SoftLayerAPIError as e:
        if e.faultCode == \
                'SoftLayer_Exception_User_Customer_LoginFailed':
            return None, None, unauthorized(resp,
                                            message=e.faultCode,
                                            details=e.faultString)

        return None, None, compute_fault(resp,
                                         message=e.faultCode,
                                         details=e.faultString)


def get_auth(req, resp, body=None):
    auth, token, err = None, None, None
    for method in [get_api_key_auth, get_password_auth]:
        auth, token, err = try_auth(method, req, resp, body=body)
        if any([auth, token, err]):
            return auth, token, err

    return auth, token, err
