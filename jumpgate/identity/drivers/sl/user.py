from jumpgate.common.error_handling import unauthorized, not_found


class UserV2(object):

    def on_get(self, req, resp, user_id):

        client = req.env['sl_client']
        account = client['Account']
        current_user_id = account.getCurrentUser(mask='mask[id]')['id']

        if int(user_id) == current_user_id:
            user = account.getCurrentUser(
                mask='mask[id,accountId,username,firstName,lastName,email]')
            user_response = {'id': str(user['id']),
                             'username': user['username'],
                             'name': user['firstName'] + " " + user['lastName'],
                             'email': user['email'],
                             'tenantId': str(user['accountId']),
                             'enabled': True
                             }
            resp.body = {'user': user_response}
        else:
            user_customer = client['User_Customer']
            try:
                parent_user_id = user_customer.getParent(
                    mask='mask[id]', id=user_id)['id']
            except Exception:
                return not_found(resp, "Invalid user ID Specified")

            if parent_user_id != current_user_id:
                return unauthorized(resp, "Unauthorized user to see details of given user")

            user_response = {}
            users = user_customer.getChildUsers(
                mask='mask[id,accountId,username,firstName,lastName,email]', id=parent_user_id)

            for user in users:
                if int(user_id) == user['id']:
                    user_response = {'id': str(user['id']),
                                     'username': user['username'],
                                     'name': user['firstName'] + " " + user['lastName'],
                                     'email': user['email'],
                                     'tenantId': str(user['accountId']),
                                     'enabled': True
                                     }
            resp.body = {'user': user_response}

