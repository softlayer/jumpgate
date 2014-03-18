import logging
LOG = logging.getLogger(__name__)


class UserV2(object):

    def on_get(self, req, resp, user_id):
        client = req.env['sl_client']
        user = client['Account'].getUsers(
            mask='mask[id,username,accountId]', filter={'users': {'id': {'operation': user_id}}})
        if not user or not len(user):
            raise Exception("User with ID '%s' Doesn't Exists" % user_id)

        user_response = {'id': str(user[0]['id']),
                         'username': str(user[0]['username']),
                         'email': str(user[0]['username']),
                         'tenantId': str(user[0]['accountId']),
                         'enabled': 'true'
                         }
        resp.body = {'user': user_response}
