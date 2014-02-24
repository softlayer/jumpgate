import time
import json
import base64

from SoftLayer import (TokenAuthentication, BasicAuthentication)

from jumpgate.common.aes import decode_aes
from jumpgate.common.exceptions import Unauthorized


def get_token_details(token, tenant_id=None):
    try:
        token_details = json.loads(decode_aes(base64.b64decode(token)))
    except (TypeError, ValueError):
        raise Unauthorized('Invalid Token')

    if time.time() > token_details['expires']:
        raise Unauthorized('Expired Token')

    if tenant_id and str(token_details['tenant_id']) != tenant_id:
        raise Unauthorized('Tenant/Token Mismatch')

    return token_details


def get_auth(token_details):
    if token_details['auth_type'] == 'api_key':
        return BasicAuthentication(token_details['username'],
                                   token_details['api_key'])
    elif token_details['auth_type'] == 'token':
        return TokenAuthentication(token_details['user_id'],
                                   token_details['api_key'])

    return None
