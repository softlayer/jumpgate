from jumpgate.common.error_handling import unauthorized,not_found


class UserV2(object):

    def on_get(self, req, resp, user_id):
        client = req.env['sl_client']
        try:
            user = client['Account'].getUsers(
            mask='mask[id,username,accountId]', filter={'users': {'id': {'operation': user_id}}})    
        except Exception:
            return unauthorized(resp,"Unauthorized User to view given user")
        if not user or not len(user):
            return not_found(resp, "Invalid user ID specified.")
        user_response = {'id': str(user[0]['id']),
                         'username': user[0]['username'],
                         'email': user[0]['username'],
                         'tenantId': str(user[0]['accountId']),
                         'enabled': True
                         }
        resp.body = {'user': user_response}
