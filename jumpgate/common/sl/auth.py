import base64
import json
import logging
import time

import jumpgate.common.utils as utils

from SoftLayer import (TokenAuthentication, BasicAuthentication)

from jumpgate.config import CONF
from jumpgate.common.aes import decode_aes
from jumpgate.common.exceptions import Unauthorized

LOG = logging.getLogger(__name__)


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
    driver_name = CONF['identity']['token_auth_driver']
    try:
        driver = utils.import_class(driver_name)
    except ImportError as e:
        LOG.info("Unable to load token auth driver %s" % (driver_name))
        raise e
    LOG.debug("Loaded token auth driver %s" % (driver_name))

    return driver().get_new_token(credentials)


def get_auth(token_details):
    if token_details['auth_type'] == 'api_key':
        return BasicAuthentication(token_details['username'],
                                   token_details['api_key'])
    elif token_details['auth_type'] == 'token':
        return TokenAuthentication(token_details['userId'],
                                   token_details['tokenHash'])

    return None
