import logging
import time

from jumpgate.common import exceptions
from jumpgate.common import utils
from jumpgate.identity.drivers import core as identity

from oslo.config import cfg
import SoftLayer


USER_MASK = 'id, username, accountId'
LOG = logging.getLogger(__name__)


def get_token_details(token, tenant_id=None):
    try:
        token_id_driver = identity.token_id_driver()
        token_details = token_id_driver.token_from_id(token)
    except (TypeError, ValueError):
        raise exceptions.Unauthorized('Invalid Key')

    if time.time() > token_details['expires']:
        raise exceptions.Unauthorized('Expired Key')

    if tenant_id and str(token_details['tenant_id']) != tenant_id:
        raise exceptions.Unauthorized('Tenant/token Mismatch')

    return token_details


def get_new_token_v3(credentials):
    token_driver = identity.token_driver()
    token_id = utils.lookup(credentials, 'auth', 'identity', 'token', 'id')
    if token_id:
        token = identity.token_id_driver().token_from_id(token_id)
        LOG.debug("token details are: %s", str(token))

        token_driver.validate_token(token)
        username = token_driver.username(token)
        credential = token_driver.credential(token)
        userinfo = {'username': username,
                    'auth_type': str(token['auth_type']),
                    'tenant_id': str(token['tenant_id']),
                    'expires': token['expires']}
        if token['auth_type'] == 'token':
            userinfo['tokenHash'] = credential
        if token['auth_type'] == 'api_key':
            userinfo['api_key'] = credential
        user = {'id': token['user_id'],
                'username': username,
                'accountId': token['tenant_id']}
        return userinfo, user

    username = utils.lookup(credentials,
                            'auth',
                            'identity',
                            'password',
                            'user',
                            'name')
    credential = utils.lookup(credentials,
                              'auth',
                              'identity',
                              'password',
                              'user',
                              'password')

    # If the 'password' is the right length, treat it as an API api_key
    if len(credential) == 64:
        endpoint = cfg.CONF['softlayer']['endpoint']
        client = SoftLayer.Client(username=username,
                                  api_key=credential,
                                  endpoint_url=endpoint,
                                  proxy=cfg.CONF['softlayer']['proxy'])
        user = client['Account'].getCurrentUser(mask=USER_MASK)

        username = token_driver.username(user)

        return {'username': username,
                'api_key': credential,
                'auth_type': 'api_key',
                'tenant_id': str(user['accountId']),
                'expires': time.time() + (60 * 60 * 24)}, user

    else:
        endpoint = cfg.CONF['softlayer']['endpoint']
        client = SoftLayer.Client(endpoint_url=endpoint,
                                  proxy=cfg.CONF['softlayer']['proxy'])
        client.auth = None
        try:
            userId, tokenHash = client.authenticate_with_password(username,
                                                                  credential)
            user = client['Account'].getCurrentUser(mask=USER_MASK)
            username = token_driver.username(user)
            return {'userId': userId,
                    'username': username,
                    'tokenHash': tokenHash,
                    'auth_type': 'token',
                    'tenant_id': str(user['accountId']),
                    'expires': time.time() + (60 * 60 * 24)}, user

        except SoftLayer.SoftLayerAPIError as e:
            if e.faultCode == 'SoftLayer_Exception_User_Customer_LoginFailed':
                raise exceptions.Unauthorized(e.faultString)
            raise


def get_auth(token_details):
    if token_details['auth_type'] == 'api_key':
        return SoftLayer.BasicAuthentication(token_details['username'],
                                             token_details['api_key'])
    elif token_details['auth_type'] == 'token':
        return SoftLayer.TokenAuthentication(token_details['user_id'],
                                             token_details['api_key'])

    return None
