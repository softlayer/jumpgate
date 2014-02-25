from SoftLayer import (TokenAuthentication, BasicAuthentication)


def get_auth(token_details):
    if token_details['auth_type'] == 'api_key':
        return BasicAuthentication(token_details['username'],
                                   token_details['api_key'])
    elif token_details['auth_type'] == 'token':
        return TokenAuthentication(token_details['user_id'],
                                   token_details['api_key'])

    return None
