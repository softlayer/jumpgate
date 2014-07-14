import json
import random
import string

import SoftLayer

from jumpgate.common import error_handling


NULL_KEY = ("AAAAB3NzaC1yc2EAAAABIwAAAIEArkwv9X8eTVK4F7pMlSt45pWoiakFk"
            "ZMwG9BjydOJPGH0RFNAy1QqIWBGWv7vS5K2tr+EEO+F8WL2Y/jK4ZkUoQgoi+n7"
            "DWQVOHsRijcS3LvtO+50Np4yjXYWJKh29JL6GHcp8o7+YKEyVUMB2CSDOP99eF9g5"
            "Q0d+1U2WVdBWQM=")


class KeypairsV2(object):
    def on_get(self, req, resp, tenant_id):
        client = req.env['sl_client']
        mgr = SoftLayer.SshKeyManager(client)
        keypairs = mgr.list_keys()

        resp.body = {
            'keypairs': [{
                'keypair': format_keypair(keypair)} for keypair in keypairs]}

    def on_post(self, req, resp, tenant_id):
        body = json.loads(req.stream.read().decode())
        try:
            name = body['keypair']['name']
            key = body['keypair'].get('public_key', generate_random_key())
        except (KeyError, TypeError):
            return error_handling.bad_request(
                resp, 'Not all fields exist to create keypair.')

        validate_result = validate_keypair_name(resp, name)
        if not validate_result:
            return

        client = req.env['sl_client']
        mgr = SoftLayer.SshKeyManager(client)

        # Make sure the key with that label doesn't already exist
        existing_keys = mgr.list_keys(label=name)
        if existing_keys:
            return error_handling.duplicate(resp, 'Duplicate key by that name')

        try:
            keypair = mgr.add_key(key, name)
            resp.body = {'keypair': format_keypair(keypair)}
        except SoftLayer.SoftLayerAPIError as e:
            if 'Unable to generate a fingerprint' in e.faultString:
                return error_handling.bad_request(resp, e.faultString)
            if 'SSH key already exists' in e.faultString:
                return error_handling.duplicate(resp, e.faultString)
            raise


class KeypairV2(object):
    def on_get(self, req, resp, tenant_id, keypair_name):
        client = req.env['sl_client']
        mgr = SoftLayer.SshKeyManager(client)
        keys = mgr.list_keys(label=keypair_name)
        if len(keys) == 0:
            return error_handling.not_found(resp, 'KeyPair not found')

        keypair = mgr.get_key(keys[0]['id'])

        resp.body = {'keypair': format_keypair(keypair)}

    def on_delete(self, req, resp, tenant_id, keypair_name):
        # keypair_name
        client = req.env['sl_client']
        mgr = SoftLayer.SshKeyManager(client)
        keys = mgr.list_keys(label=keypair_name)
        if len(keys) == 0:
            return error_handling.not_found(resp, 'KeyPair not Found')

        mgr.delete_key(keys[0]['id'])
        resp.status = 202


def format_keypair(keypair):
    return {
        'fingerprint': keypair['fingerprint'],
        'name': keypair['label'],
        'public_key': keypair['key'],
        # TODO(imkarrer) properly set this to current tenant_id
        'user_id': '1234'
    }


def generate_random_key():
    chars = string.digits + string.ascii_letters
    key = "".join([random.choice(chars) for _ in range(8)])
    return "ssh-rsa %s %s@invalid" % (NULL_KEY, key)


def validate_keypair_name(resp, key_name):
    safechars = "_- " + string.digits + string.ascii_letters
    clean_value = "".join(x for x in key_name if x in safechars)
    if clean_value != key_name:
        error_handling.bad_request(
            resp, 'Keypair name contains unsafe characters')
        return False

    if not 0 < len(key_name) < 256:
        error_handling.bad_request(
            resp, 'Keypair name must be between 1 and 255 characters long')
        return False

    return True
