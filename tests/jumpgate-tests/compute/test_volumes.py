import unittest
import falcon
from falcon.testing import helpers
import mock
import SoftLayer

from jumpgate.compute.drivers.sl import volumes


TENANT_ID = 333333
INSTANCE_ID = 7890782
VOLUME_ID = '3887490'


def get_client_env(**kwargs):
    client = mock.MagicMock()
    env = helpers.create_environ(**kwargs)
    env['sl_client'] = client
    return client, env


class TestOSVolumeAttachmentsV2(unittest.TestCase):

    def perform_attach_action(self, body_str, tenant_id, instance_id):
        self.client, self.env = get_client_env(body=body_str)
        self.vg_clientMock = self.client['Virtual_Guest']
        self.vdi_clientMock = self.client['Virtual_Disk_Image']
        self.req = falcon.Request(self.env)
        self.resp = falcon.Response()
        instance = volumes.OSVolumeAttachmentsV2()
        instance.on_post(self.req, self.resp, tenant_id, instance_id)

    def test_on_post(self):
        body_str = ('{"volumeAttachment": '
                    '{"device": null, "volumeId": "3887490"}}')
        self.perform_attach_action(body_str, TENANT_ID, INSTANCE_ID)
        self.vg_clientMock.attachDiskImage.assert_called_with("3887490",
                                                              id=INSTANCE_ID)
        self.assertEquals(list(self.resp.body.keys()), ['volumeAttachment'])
        self.assertEquals('device' in self.resp.body['volumeAttachment'],
                          True)
        self.assertEquals('id' in self.resp.body['volumeAttachment'], True)
        self.assertEquals('serverId' in self.resp.body['volumeAttachment'],
                          True)
        self.assertEquals('volumeId' in self.resp.body['volumeAttachment'],
                          True)
        self.assertEquals(self.resp.status, 202)

    def test_on_post_fail_empty_body(self):
        body_str = '{}'
        self.perform_attach_action(body_str, TENANT_ID, INSTANCE_ID)
        self.assertEquals(self.resp.body, {'badRequest':
                                           {'message':
                                            'Malformed request body',
                                            'code': '400'}})

    def test_on_post_fail_missing_volumeAttachment(self):
        body_str = '{"random_key": "random_value"}'
        self.perform_attach_action(body_str, TENANT_ID, INSTANCE_ID)
        self.assertEquals(self.resp.body, {'badRequest':
                                           {'message':
                                            'Malformed request body',
                                            'code': '400'}})

    def test_on_post_fail_missing_volumeID(self):
        body_str = ('{"volumeAttachment": '
                    '{"device": null}}')
        self.perform_attach_action(body_str, TENANT_ID, INSTANCE_ID)
        self.assertEquals(self.resp.body, {'badRequest':
                                           {'message':
                                            'Malformed request body',
                                            'code': '400'}})

    def test_on_post_fail_instance_id_not_number(self):
        body_str = ('{"volumeAttachment": '
                    '{"device": null, "volumeId": "3887490"}}')
        self.perform_attach_action(body_str, TENANT_ID, 'not a number')
        self.assertEquals(self.resp.body, {'notFound':
                                           {'message':
                                            'Invalid instance ID specified.',
                                            'code': '404'}})

    def test_on_post_fail_volume_id_too_long(self):
        body_str = ('{"volumeAttachment": '
                    '{"device": null, "volumeId": '
                    '"0123456789012345678901234567890123456789"}}')
        self.perform_attach_action(body_str, TENANT_ID, INSTANCE_ID)
        self.assertEquals(self.resp.body, {'badRequest':
                                           {'message':
                                            'Malformed request body',
                                            'code': '400'}})

    def test_on_post_fail_disk_already_attach_this_guest(self):
        body_str = ('{"volumeAttachment": '
                    '{"device": null, "volumeId": "3887490"}}')
        client, env = get_client_env(body=body_str)
        vg_clientMock = client['Virtual_Guest']
        vdi_clientMock = client['Virtual_Disk_Image']
        vdi_clientMock.getObject.return_value = {'blockDevices':
                                                 [{'guestId': INSTANCE_ID}]}
        req = falcon.Request(env)
        resp = falcon.Response()
        instance = volumes.OSVolumeAttachmentsV2()
        instance.on_post(req, resp, TENANT_ID, INSTANCE_ID)
        self.assertEquals(resp.body, {'volumeFault':
                                      {'message':
                                       'The requested disk image is already'
                                       ' attached to this guest.',
                                       'code': '400'}})

    def test_on_post_fail_disk_already_attach_another_guest(self):
        body_str = ('{"volumeAttachment": '
                    '{"device": null, "volumeId": "3887490"}}')
        client, env = get_client_env(body=body_str)
        vg_clientMock = client['Virtual_Guest']
        vdi_clientMock = client['Virtual_Disk_Image']
        vdi_clientMock.getObject.return_value = {'blockDevices':
                                                 [{'guestId': 1234567}]}
        req = falcon.Request(env)
        resp = falcon.Response()
        instance = volumes.OSVolumeAttachmentsV2()
        instance.on_post(req, resp, TENANT_ID, INSTANCE_ID)
        self.assertEquals(resp.body, {'volumeFault':
                                      {'message':
                                       'The requested disk image is already'
                                       ' attached to another guest.',
                                       'code': '400'}})

    def test_on_post_fail_vdi_client_exception(self):
        body_str = ('{"volumeAttachment": '
                    '{"device": null, "volumeId": "3887490"}}')
        client, env = get_client_env(body=body_str)
        vg_clientMock = client['Virtual_Guest']
        vdi_clientMock = client['Virtual_Disk_Image']
        vdi_clientMock.getObject.side_effect = Exception('No Object!')
        req = falcon.Request(env)
        resp = falcon.Response()
        instance = volumes.OSVolumeAttachmentsV2()
        instance.on_post(req, resp, TENANT_ID, INSTANCE_ID)
        self.assertEquals(resp.body, {'volumeFault':
                                      {'message':
                                       'No Object!',
                                       'code': '400'}})

    def test_on_post_fail_vdi_client_exception(self):
        body_str = ('{"volumeAttachment": '
                    '{"device": null, "volumeId": "3887490"}}')
        client, env = get_client_env(body=body_str)
        vg_clientMock = client['Virtual_Guest']
        vdi_clientMock = client['Virtual_Disk_Image']
        vg_clientMock.checkHostDiskAvailability.return_value = False
        req = falcon.Request(env)
        resp = falcon.Response()
        instance = volumes.OSVolumeAttachmentsV2()
        instance.on_post(req, resp, TENANT_ID, INSTANCE_ID)
        self.assertEquals(resp.body, {'volumeFault':
                                      {'message':
                                       'Action causes migration to a new '
                                        'host. Migration is not allowed.',
                                       'code': '400'}})

    def perform_volume_list(self, tenant_id, instance_id):
        self.client, self.env = get_client_env()
        self.vg_clientMock = self.client['Virtual_Guest']
        self.vdi_clientMock = self.client['Virtual_Disk_Image']
        self.req = falcon.Request(self.env)
        self.resp = falcon.Response()
        instance = volumes.OSVolumeAttachmentsV2()
        instance.on_get(self.req, self.resp, tenant_id, instance_id)

    def test_on_get(self):
        self.client, self.env = get_client_env()
        self.vg_clientMock = self.client['Virtual_Guest']
        self.vg_clientMock.getBlockDevices.return_value = [{'diskImage':
                                                            {'type':
                                                             {'keyName':
                                                              'not SWAP'},
                                                             'id': '0123456'}
                                                            }]
        self.vdi_clientMock = self.client['Virtual_Disk_Image']
        self.req = falcon.Request(self.env)
        self.resp = falcon.Response()
        instance = volumes.OSVolumeAttachmentsV2()
        instance.on_get(self.req, self.resp, TENANT_ID, INSTANCE_ID)
        self.assertEquals(list(self.resp.body.keys()), ['volumeAttachments'])
        self.assertEquals('device' in self.resp.body['volumeAttachments'][0],
                          True)
        self.assertEquals('id' in self.resp.body['volumeAttachments'][0],
                          True)
        self.assertEquals('serverId' in self.resp.body['volumeAttachments'][0],
                          True)
        self.assertEquals('volumeId' in self.resp.body['volumeAttachments'][0],
                          True)

    def test_on_get_fail_instance_id_not_a_number(self):
        self.perform_volume_list(TENANT_ID, 'not a number')
        self.assertEquals(self.resp.body, {'notFound':
                                           {'message':
                                            'Invalid instance ID specified.',
                                            'code': '404'}})

    def test_on_get_fail_block_devices_exception(self):
        client, env = get_client_env()
        vg_clientMock = client['Virtual_Guest']
        gbdMock = vg_clientMock.getBlockDevices
        gbdMock.side_effect = SoftLayer.SoftLayerAPIError(404,
                                                          'No Block Devices',
                                                          None)
        vdi_clientMock = client['Virtual_Disk_Image']
        req = falcon.Request(env)
        resp = falcon.Response()
        instance = volumes.OSVolumeAttachmentsV2()
        instance.on_get(req, resp, TENANT_ID, INSTANCE_ID)
        self.assertEquals(resp.body, {'volumeFault':
                                      {'message': 'No Block Devices',
                                       'code': '500'}})

class TestOSVolumeAttachmentV2(unittest.TestCase):

    def perform_detach_action(self, tenant_id, instance_id, volume_id):
        self.client, self.env = get_client_env()
        self.vg_clientMock = self.client['Virtual_Guest']
        self.vdi_clientMock = self.client['Virtual_Disk_Image']
        self.req = falcon.Request(self.env)
        self.resp = falcon.Response()
        instance = volumes.OSVolumeAttachmentV2()
        instance.on_delete(self.req, self.resp, tenant_id,
                           instance_id, volume_id)

    def test_on_delete(self):
        client, env = get_client_env()
        vg_clientMock = client['Virtual_Guest']
        vdi_clientMock = client['Virtual_Disk_Image']
        vdi_clientMock.getObject.return_value = {'blockDevices':
                                                 [{'guestId': INSTANCE_ID}]}
        req = falcon.Request(env)
        resp = falcon.Response()
        instance = volumes.OSVolumeAttachmentV2()
        instance.on_delete(req, resp, TENANT_ID, INSTANCE_ID, VOLUME_ID)
        vg_clientMock.detachDiskImage.assert_called_with(VOLUME_ID,
                                                         id=INSTANCE_ID)
        self.assertEquals(resp.status, 202)

    def test_on_delete_fail_instance_id_not_a_number(self):
        self.perform_detach_action(TENANT_ID, 'not a number', VOLUME_ID)
        self.assertEquals(self.resp.body, {'notFound': {'message':
                                                        'Invalid instance'
                                                        ' ID specified.',
                                                        'code': '404'}})

    def test_on_delete_fail_volume_id_too_long(self):
        self.perform_detach_action(TENANT_ID, INSTANCE_ID,
                                   '0123456789012345678901234567890123456789')
        self.assertEquals(self.resp.body, {'badRequest':
                                           {'message': 'Malformed request '
                                            'body', 'code': '400'}})

    def test_on_delete_fail_detach_exception(self):
        client, env = get_client_env()
        vg_clientMock = client['Virtual_Guest']
        deiMock = vg_clientMock.detachDiskImage
        deiMock.side_effect = (SoftLayer.SoftLayerAPIError(404,
                                                           'Detach Error',
                                                           None))
        vdi_clientMock = client['Virtual_Disk_Image']
        vdi_clientMock.getObject.return_value = {'blockDevices':
                                                 [{'guestId': INSTANCE_ID}]}
        req = falcon.Request(env)
        resp = falcon.Response()
        instance = volumes.OSVolumeAttachmentV2()
        instance.on_delete(req, resp, TENANT_ID, INSTANCE_ID, VOLUME_ID)
        vg_clientMock.detachDiskImage.assert_called_with(VOLUME_ID,
                                                         id=INSTANCE_ID)
        self.assertEquals(resp.body, {'volumeFault':
                                      {'message': 'Detach Error',
                                       'code': '500'}})

    def test_on_delete_fail_detach_getObject_exception(self):
        client, env = get_client_env()
        vg_clientMock = client['Virtual_Guest']
        vdi_clientMock = client['Virtual_Disk_Image']
        vdi_clientMock.getObject.side_effect = (SoftLayer.
                                                SoftLayerAPIError(404,
                                                                  'No Object',
                                                                  None))
        req = falcon.Request(env)
        resp = falcon.Response()
        instance = volumes.OSVolumeAttachmentV2()
        instance.on_delete(req, resp, TENANT_ID, INSTANCE_ID, VOLUME_ID)
        vdi_clientMock.getObject.assert_called_with(id=VOLUME_ID,
                                                    mask='blockDevices')
        self.assertEquals(resp.body, {'volumeFault':
                                      {'message': 'No Object',
                                       'code': '500'}})

    def test_on_delete_fail_disk_already_attached(self):
        client, env = get_client_env()
        vg_clientMock = client['Virtual_Guest']
        vdi_clientMock = client['Virtual_Disk_Image']
        vdi_clientMock.getObject.return_value = {'blockDevices':
                                                 [{'guestId': '0123456'}]}
        req = falcon.Request(env)
        resp = falcon.Response()
        instance = volumes.OSVolumeAttachmentV2()
        instance.on_delete(req, resp, TENANT_ID, INSTANCE_ID, VOLUME_ID)
        self.assertEquals(resp.body, {'volumeFault':
                                      {'message': 'The requested disk image '
                                       'is attached to another guest and '
                                       'cannot be detached.',
                                       'code': '400'}})

    def perform_get_vol_details(self, tenant_id, instance_id, volume_id):
        self.client, self.env = get_client_env()
        self.vg_clientMock = self.client['Virtual_Guest']
        self.vdi_clientMock = self.client['Virtual_Disk_Image']
        self.req = falcon.Request(self.env)
        self.resp = falcon.Response()
        instance = volumes.OSVolumeAttachmentV2()
        instance.on_get(self.req, self.resp, tenant_id,
                           instance_id, volume_id)

    def test_on_get(self):
        client, env = get_client_env()
        vg_clientMock = client['Virtual_Guest']
        vg_clientMock.getBlockDevices.return_value = [{'diskImage':
                                                       {'type':
                                                        {'keyName':
                                                         'not SWAP'},
                                                        'id': VOLUME_ID}}]
        vdi_clientMock = client['Virtual_Disk_Image']
        req = falcon.Request(env)
        resp = falcon.Response()
        instance = volumes.OSVolumeAttachmentV2()
        instance.on_get(req, resp, TENANT_ID, INSTANCE_ID, VOLUME_ID)
        self.assertEquals(list(resp.body.keys()), ['volumeAttachment'])
        self.assertEquals('device' in resp.body['volumeAttachment'],
                          True)
        self.assertEquals('id' in resp.body['volumeAttachment'],
                          True)
        self.assertEquals('serverId' in resp.body['volumeAttachment'],
                          True)
        self.assertEquals('volumeId' in resp.body['volumeAttachment'],
                          True)

    def test_on_get_fail_instance_id_not_a_number(self):
        self.perform_get_vol_details(TENANT_ID, 'not a number', VOLUME_ID)
        self.assertEquals(self.resp.body, {'notFound':
                                           {'message': 'Invalid instance ID '
                                            'specified.', 'code': '404'}})

    def test_on_get_fail_volume_id_too_long(self):
        self.perform_get_vol_details(TENANT_ID, INSTANCE_ID,
                                     '0123456789012345678901234567890123456')
        self.assertEquals(self.resp.body, {'badRequest':
                                           {'message': 'Malformed request '
                                            'body', 'code': '400'}})

    def test_on_get_fail_invalid_volume_id(self):
        client, env = get_client_env()
        vg_clientMock = client['Virtual_Guest']
        vg_clientMock.getBlockDevices.return_value = [{'diskImage':
                                                       {'type':
                                                        {'keyName':
                                                         'not SWAP'},
                                                        'id': '0123456'}}]
        vdi_clientMock = client['Virtual_Disk_Image']
        req = falcon.Request(env)
        resp = falcon.Response()
        instance = volumes.OSVolumeAttachmentV2()
        instance.on_get(req, resp, TENANT_ID, INSTANCE_ID, VOLUME_ID)
        self.assertEquals(self.resp.body, {'notFound':
                                           {'message': 'Invalid instance ID '
                                            'specified.', 'code': '404'}})

    def test_on_get_fail_invalid_volume_id(self):
        client, env = get_client_env()
        vg_clientMock = client['Virtual_Guest']
        gbdMock = vg_clientMock.getBlockDevices
        gbdMock.side_effect = SoftLayer.SoftLayerAPIError(404,
                                                          'No Block Devices',
                                                          None)
        vdi_clientMock = client['Virtual_Disk_Image']
        req = falcon.Request(env)
        resp = falcon.Response()
        instance = volumes.OSVolumeAttachmentV2()
        instance.on_get(req, resp, TENANT_ID, INSTANCE_ID, VOLUME_ID)
        self.assertEquals(resp.body, {'volumeFault':
                                      {'message': 'No Block Devices',
                                       'code': '500'}})
