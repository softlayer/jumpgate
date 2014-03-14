

class UserV2(object):

    def on_get(self, req, resp, user_id):
        client = req.env['sl_client']
        account = client['Account'].getCurrentUser()

        user = {'id': str(account['id']),
                'name': str(account['firstName']),
                'username': str(account['username']),
                'email': str(account['email']),
                'tenantId': str(account['accountId']),
                'enabled': 'true'
                }

        resp.body = {'user': user}
