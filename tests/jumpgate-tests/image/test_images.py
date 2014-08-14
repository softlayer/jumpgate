import mock
import unittest

import falcon
from falcon.testing import helpers
import SoftLayer

from jumpgate.image.drivers.sl import images


def get_client_env(**kwargs):
    client = mock.MagicMock()
    env = helpers.create_environ(**kwargs)
    env['sl_client'] = client
    return client, env


class TestImageV1(unittest.TestCase):

    def setUp(self):
        self.req = mock.MagicMock()
        self.resp = mock.MagicMock()
        self.img = mock.MagicMock()
        self.app = mock.MagicMock()

    def test_on_get(self):
        client, env = get_client_env()
        vgbdtg = client['Virtual_Guest_Block_Device_Template_Group']
        vgbdtg.getObject.return_value = {
            'globalIdentifier': 'uuid',
            'blockDevicesDiskSpaceTotal': 1000,
            'name': 'some image',
        }

        req = falcon.Request(env)
        resp = falcon.Response()

        images.ImageV1(self.app).on_get(req, resp, '1')

        image = resp.body['image']
        self.assertEquals(image['id'], 'uuid')
        self.assertEquals(image['name'], 'some image')
        self.assertEquals(image['size'], 1000)

    def test_on_get_fail(self):
        client, env = get_client_env()
        vgbdtg = client['Virtual_Guest_Block_Device_Template_Group']
        error = SoftLayer.SoftLayerAPIError(
            "SoftLayer_Exception_ObjectNotFound",
            "Unable to find object with id of '1'")
        vgbdtg.getObject.side_effect = error

        req = falcon.Request(env)
        resp = falcon.Response()

        self.assertRaises(SoftLayer.SoftLayerAPIError,
                          images.ImageV1(self.app).on_get, req, resp, '1')

    def test_get_v1_image_details_dict(self):
        expected_keys = [
            'status',
            'updated',
            'created',
            'id',
            'progress',
            'metadata',
            'size',
            'OS-EXT-IMG-SIZE:size',
            'container_format',
            'disk_format',
            'is_public',
            'protected',
            'owner',
            'minDisk',
            'minRam',
            'name',
            'links',
        ]
        app, req, image, tenant_id = (mock.MagicMock(),
                                      mock.MagicMock(),
                                      mock.MagicMock(),
                                      mock.MagicMock())
        res = images.get_v1_image_details_dict(app, req, image, tenant_id)
        self.assertEquals(set(expected_keys), set(res.keys()))

    def test_get_v1_image_details_dict_fail(self):
        app, req, image, tenant_id = (mock.MagicMock(),
                                      mock.MagicMock(),
                                      None,
                                      mock.MagicMock())
        res = images.get_v1_image_details_dict(app, req, image, tenant_id)
        self.assertFalse(res)


class TestImagesV2(unittest.TestCase):

    def setUp(self):
        self.req, self.resp = mock.MagicMock(), mock.MagicMock()
        self.app = mock.MagicMock()

    def test_get_v2_image_details_dict(self):
        expected_keys = [
            'status',
            'updated',
            'created',
            'id',
            'progress',
            'metadata',
            'size',
            'container_format',
            'disk_format',
            'is_public',
            'protected',
            'owner',
            'minDisk',
            'minRam',
            'name',
            'visibility',
            'links',
        ]
        app, req, image, tenant_id = (mock.MagicMock(),
                                      mock.MagicMock(),
                                      mock.MagicMock(),
                                      mock.MagicMock())
        res = images.get_v2_image_details_dict(app, req, image, tenant_id)
        self.assertEquals(set(expected_keys), set(res.keys()))

    def test_get_v2_image_details_dict_fail(self):
        app, req, image, tenant_id = (mock.MagicMock(),
                                      mock.MagicMock(),
                                      None,
                                      mock.MagicMock())
        res = images.get_v2_image_details_dict(app, req, image, tenant_id)
        self.assertFalse(res)

    def test_on_get(self):
        client, env = get_client_env()
        vgbdtg = client['Virtual_Guest_Block_Device_Template_Group']
        vgbdtg.getPublicImages.return_value = [{
            'globalIdentifier': 'uuid',
            'blockDevicesDiskSpaceTotal': 1000,
            'name': 'some image',
        }]
        client['Account'].getPrivateBlockDeviceTemplateGroups.return_value = [{
            'globalIdentifier': 'uuid2',
            'blockDevicesDiskSpaceTotal': 2000,
            'name': 'some other image',
        }]

        req = falcon.Request(env)
        resp = falcon.Response()

        images.ImagesV2(self.app).on_get(req, resp)

        self.assertEquals(resp.status, 200)
        self.assertEquals(len(resp.body['images']), 2)
        image1 = resp.body['images'][0]
        self.assertEquals(image1['id'], 'uuid')
        self.assertEquals(image1['name'], 'some image')
        self.assertEquals(image1['size'], 1000)

        image2 = resp.body['images'][1]
        self.assertEquals(image2['id'], 'uuid2')
        self.assertEquals(image2['name'], 'some other image')
        self.assertEquals(image2['size'], 2000)

    def test_on_get_with_name_filter(self):
        client, env = get_client_env(query_string='name=imageA')
        vgbdtg = client['Virtual_Guest_Block_Device_Template_Group']
        vgbdtg.getPublicImages.return_value = [{
            'globalIdentifier': 'uuid',
            'blockDevicesDiskSpaceTotal': 1000,
            'name': 'imageA',
        }]
        client['Account'].getPrivateBlockDeviceTemplateGroups.return_value = [{
            'globalIdentifier': 'uuid2',
            'blockDevicesDiskSpaceTotal': 2000,
            'name': 'imageB',
        }]

        # 1. There is one image pass the filter and returned in result.
        req = falcon.Request(env)
        resp = falcon.Response()

        images.ImagesV2(self.app).on_get(req, resp)

        self.assertEquals(resp.status, 200)
        self.assertEquals(len(resp.body['images']), 1)
        image1 = resp.body['images'][0]
        self.assertEquals(image1['id'], 'uuid')
        self.assertEquals(image1['name'], 'imageA')
        self.assertEquals(image1['size'], 1000)

        # 2. There is no any image could pass the filter and been returned.
        __client, env = get_client_env(query_string='name=imageX')
        req = falcon.Request(env)
        resp = falcon.Response()

        images.ImagesV2(self.app).on_get(req, resp)

        self.assertEquals(resp.status, 200)
        self.assertEquals(len(resp.body['images']), 0)
