import SoftLayer

from jumpgate.common import error_handling


class UserV2(object):

    def on_get(self, req, resp, user_id, **kwargs):

        if 'mask' not in kwargs:
            items = set([
                'id',
                'username',
                'firstName',
                'accountId',
                'email',
            ])
            kwargs['mask'] = "mask[%s]" % ','.join(items)

        client = req.env['sl_client']

        try:
            user = client['User_Customer'].getObject(id=user_id,
                                                     **kwargs)
        except SoftLayer.SoftLayerAPIError as ex:
            if ex.faultCode == 'SoftLayer_Exception_ObjectNotFound':
                return error_handling.not_found(resp,
                                                "Invalid User ID specified")
            raise
        fieldMap = {
            # SL-Field : OpenStack-Field
            'id': 'id',
            'username': 'username',
            'email': 'email',
            'accountId': 'tenantId',
            'firstName': 'name'
        }
        user_detail = {}
        for field in fieldMap.keys():
            if user.get(field, None):
                user_detail[fieldMap[field]] = user[field]
        resp.body = {
            'user': user_detail
        }
