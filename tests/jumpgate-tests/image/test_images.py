from mock import MagicMock, patch
from jumpgate.image.drivers.sl.images import (SLImages, ImagesV2, ImageV1,
                                              get_v1_image_details_dict,
                                              get_v2_image_details_dict,
                                              )
import SoftLayer
import unittest


class TestImageV1(unittest.TestCase):

    def setUp(self):
        self.req, self.resp, self.img = MagicMock(), MagicMock(), MagicMock()
        self.app = MagicMock()
        self.instance = ImageV1(self.app)

    def test_init(self):
        self.assertEquals(self.instance.app, self.app)

    @patch('jumpgate.image.drivers.sl.images.SLImages')
    def test_on_get(self, mockSLImage):
        dict = {'image': None}
        self.instance.on_get(self.req, self.resp, self.img)
        self.assertEquals(dict.keys(), self.resp.body.keys())
        self.assertEquals(self.resp.status, 200)

    @patch('jumpgate.image.drivers.sl.images.SLImages.get_image')
    def test_on_get_fail(self, mockGetImage):
        mockGetImage.return_value = None
        self.instance.on_get(self.req, self.resp, self.img)
        self.assertTrue('notFound' in self.resp.body)

    def test_get_v1_image_details_dict(self):
        dict = {
            'status': None,
            'updated': None,
            'created': None,
            'id': None,
            'progress': None,
            'metadata': None,
            'size': None,
            'OS-EXT-IMG-SIZE:size': None,
            'container_format': None,
            'disk_format': None,
            'is_public': None,
            'protected': None,
            'owner': None,
            'minDisk': None,
            'minRam': None,
            'name': None,
            'links': [{'href': None,
                       'rel': None},
                      {'href': None,
                       'rel': None}]}
        app, req, image, tenant_id = (
            MagicMock(), MagicMock(), MagicMock(), MagicMock())
        res = get_v1_image_details_dict(app, req, image, tenant_id)
        self.assertEquals(set(dict.keys()), set(res.keys()))

    def test_get_v1_image_details_dict_fail(self):
        app, req, image, tenant_id = (
            MagicMock(), MagicMock(), None, MagicMock())
        res = get_v1_image_details_dict(app, req, image, tenant_id)
        self.assertFalse(res)

    def tearDown(self):
        self.req, self.resp, self.img, self.app, self.instance = (None, None,
                                                                  None, None,
                                                                  None,)


class TestImagesV2(unittest.TestCase):

    def setUp(self):
        self.req, self.resp = MagicMock(), MagicMock()
        self.app = MagicMock()
        self.instance = ImagesV2(self.app)

    def test_init(self):
        self.assertEquals(self.app, self.instance.app)

    def test_get_v2_image_details_dict(self):
        dict = {
            'status': None,
            'updated': None,
            'created': None,
            'id': None,
            'progress': None,
            'metadata': None,
            'size': None,
            'container_format': None,
            'disk_format': None,
            'is_public': None,
            'protected': None,
            'owner': None,
            'minDisk': None,
            'minRam': None,
            'name': None,
            'visibility': None,
            'links': [{'href': None,
                       'rel': None},
                      {'href': None,
                       'rel': None}]}
        app, req, image, tenant_id = (
            MagicMock(), MagicMock(), MagicMock(), MagicMock())
        res = get_v2_image_details_dict(app, req, image, tenant_id)
        self.assertEquals(set(dict.keys()), set(res.keys()))

    def test_get_v2_image_details_dict_fail(self):
        app, req, image, tenant_id = (
            MagicMock(), MagicMock(), None, MagicMock())
        res = get_v2_image_details_dict(app, req, image, tenant_id)
        self.assertFalse(res)

    def test_on_get(self):
        dict = {'images': {'name': None}}
        self.req.get_param('limit').return_value = None
        self.req.get_param('marker').return_value = None
        self.instance.on_get(self.req, self.resp)
        self.assertEquals(self.resp.body.keys(), dict.keys())
        self.assertEquals(self.resp.status, 200)

    def tearDown(self):
        self.req, self.resp, self.app, self.instance = (None, None, None, None)


class TestSLImages(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.instance = SLImages(self.client)
        self.name = 'foo'
        self.guid = '1234'
        self.limit = '5555'
        self.marker = '4321'

    def test_init(self):
        self.assertEquals(self.client, self.instance.client)

    @patch('SoftLayer.utils.query_filter')
    def test_get_private_images(self, queryMock):
        retExpected = self.client['Account']
        retExpected.getPrivateBlockDeviceTemplateGroups.return_value = []
        ret = self.instance.get_private_images(self.guid, self.name,
                                               self.limit, self.marker)
        queryMock.assert_any_call(self.name)
        queryMock.assert_any_call(self.guid)
        queryMock.assert_any_call('> %s' % self.marker)
        self.assertEquals(type(ret), list)

    @patch('SoftLayer.utils.query_filter')
    def test_get_public_image(self, queryMock):
        retExpected = self.client['Virtual_Guest_Block_Device_Template_Group']
        retExpected.getPrivateBlockDeviceTemplateGroups.return_value = []
        ret = self.instance.get_private_images(self.guid, self.name,
                                               self.limit, self.marker)
        queryMock.assert_any_call(self.name)
        queryMock.assert_any_call(self.guid)
        queryMock.assert_any_call('> %s' % self.marker)
        self.assertEquals(type(ret), list)

    def tearDown(self):
        self.client, self.instance, self.name = None, None, None
        self.guid, self.limit, self.marker = None, None, None
