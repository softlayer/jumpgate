from jumpgate.common.error_handling import not_found


class UserV2(object):

    def on_get(self, req, resp, user_id, **kwargs):

        if 'mask' not in kwargs:
            items = set([
                'id',
                'username',
                'firstName',
                'lastName',
                'accountId',
                'email',
            ])
            kwargs['mask'] = "mask[%s]" % ','.join(items)

        client = req.env['sl_client']
        current_user = client['Account'].getCurrentUser(**kwargs)

        # User can retrieve details of itself and it's subuser only
        if int(user_id) < current_user['id']:
            return not_found(resp, "Invalid User ID specified")

        try:
            user = client['User_Customer'].getObject(id=user_id,
                                                     **kwargs)
        except Exception:
            return not_found(resp, "Invalid User ID specified")

        resp.body = {
            'user':
            {
                'id': str(user['id']),
                'username': user['username'],
                'name': user['firstName'] + " " + user['lastName'],
                'email': user['email'],
                'tenantId': str(user['accountId']),
                'enabled': True
            }
        }
