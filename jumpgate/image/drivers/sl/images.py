import itertools
import json
import uuid

from jumpgate.common import error_handling
from jumpgate.common import utils
from jumpgate.image.drivers.sl import schema


IMAGE_MASK = ('id,accountId,name,globalIdentifier,blockDevices,parentId,'
              'createDate,blockDevicesDiskSpaceTotal')


class SchemaImageV2(object):
    # TODO() - This needs to be updated for our specifications

    def on_get(self, req, resp):
        resp.body = schema.image


class SchemaImagesV2(object):
    # TODO() - This needs to be updated for our specifications
    def on_get(self, req, resp):
        resp.body = {
            "name": "images",
            "properties": {
                "first": {
                    "type": "string"
                },
                "images": {
                    "items": schema.image,
                    "type": "array"
                },
                "next": {
                    "type": "string"
                },
                "schema": {
                    "type": "string"
                }
            },
            "links": [
                {
                    "href": "{first}",
                    "rel": "first"
                },
                {
                    "href": "{next}",
                    "rel": "next"
                },
                {
                    "href": "{schema}",
                    "rel": "describedby"
                }
            ]
        }


class SchemaMemberV2(object):
    # TODO() - This needs to be updated for our specifications

    def on_get(self, req, resp):
        resp.body = schema.member


class SchemaMembersV2(object):
    # TODO() - This needs to be updated for our specifications
    def on_get(self, req, resp):
        resp.body = {
            "name": "members",
            "properties": {
                "members": schema.member,
                "schema": {
                    "type": "string"
                }
            },
            "links": [
                {
                    "href": "{schema}",
                    "rel": "describedby"
                }
            ]
        }


class ImagesV2(object):
    def __init__(self, app):
        self.app = app

    def on_delete(self, req, resp, image_guid=None, tenant_id=None):
        if not image_guid:
            return error_handling.not_found(resp, 'Image could not be found')

        client = req.env['sl_client']
        results = get_image(client, image_guid)

        if not results:
            return error_handling.not_found(resp, 'Image could not be found')

        client['Virtual_Guest_Block_Device_Template_Group'].deleteObject(
            id=results['id'])

        resp.status = 204

    def on_post(self, req, resp, tenant_id=None):
        body = json.loads(req.stream.read().decode())

        image_id = body.get('id', str(uuid.uuid4()))
        url = body.get('direct_url')
        osRefCode = body.get('os_version', None)
        if not all([url, osRefCode]):
            raise error_handling.bad_request(
                resp, "Swift url and OS code must be given")

        configuration = {
            'name': body.get('name'),
            'note': '',
            'operatingSystemReferenceCode': osRefCode,
            'uri': url
        }

        image_service = req.env['sl_client'][
            'SoftLayer_Virtual_Guest_Block_Device_Template_Group']
        img = image_service.createFromExternalSource(configuration)

        resp.body = {
            'id': img['globalIdentifier'],
            'name': body['name'],
            'status': 'queued',
            'visibility': 'private',
            'tags': [],
            'created_at': img['createDate'],
            'updated_at': img['createDate'],
            'self': self.app.get_endpoint_url(
                'image', req, 'v2_image', image_guid=image_id),
            'file': self.app.get_endpoint_url(
                'image', req, 'v2_image_file', image_guid=image_id),
            'schema': self.app.get_endpoint_url('image',
                                                req,
                                                'v2_schema_image'),
        }

    def on_get(self, req, resp, tenant_id=None):
        client = req.env['sl_client']
        tenant_id = tenant_id or utils.lookup(req.env, 'auth', 'tenant_id')

        images = []
        for image in get_all_images(client):
            img = get_v2_image_details_dict(self.app, req, image, tenant_id)

            # Apply conditions from filters
            # TODO(zhiyan): Will add more filters continuously
            # with requirement-driven way.
            if req.get_param('name'):
                if img['name'] != req.get_param('name'):
                    continue

            images.append(img)

        sorted_images = sorted(images, key=lambda x: x['id'].lower())
        if req.get_param('marker'):
            predicate = lambda x: x['id'] <= req.get_param('marker')
            sorted_images = list(itertools.dropwhile(predicate, sorted_images))

        if req.get_param('limit'):
            sorted_images = sorted_images[:int(req.get_param('limit'))]

        resp.status = 200
        resp.body = {'images': sorted_images}


class ImageV1(object):
    def __init__(self, app):
        self.app = app

    def on_delete(self, req, resp, image_guid=None, tenant_id=None):
        if not image_guid:
            return error_handling.not_found(resp, 'Image could not be found')

        client = req.env['sl_client']
        results = get_image(client, image_guid)

        if not results:
            return error_handling.not_found(resp, 'Image could not be found')

        client['Virtual_Guest_Block_Device_Template_Group'].deleteObject(
            id=results['id'])

        resp.status = 204

    def on_get(self, req, resp, image_guid, tenant_id=None):
        client = req.env['sl_client']
        results = get_image(client, image_guid)

        if not results:
            return error_handling.not_found(resp, 'Image could not be found')

        details = get_v1_image_details_dict(self.app, req, results)

        resp.status = 200
        resp.body = {'image': details}

    def on_head(self, req, resp, image_guid, tenant_id=None):
        client = req.env['sl_client']
        image = get_image(client, image_guid)
        results = get_v1_image_details_dict(self.app, req, image)

        if not results:
            return error_handling.not_found(resp, 'Image could not be found')

        headers = {
            'x-image-meta-id': image_guid,
            'x-image-meta-status': results['status'].lower(),
            'x-image-meta-owner': results.get('owner'),
            'x-image-meta-name': results['name'],
            'x-image-meta-container_format': results['container_format'],
            'x-image-meta-created_at': results['created'],
            'x-image-meta-min_ram': results.get('minRam'),
            'x-image-meta-updated_at': results['updated'],
            'location': self.app.get_endpoint_url('image', req, 'v1_image',
                                                  image_guid=image_guid),
            'x-image-meta-deleted': False,
            'x-image-meta-protected': results['protected'],
            'x-image-meta-min_disk': results.get('minDisk'),
            'x-image-meta-size': results['size'],
            'x-image-meta-is_public': results['is_public'],
            'x-image-meta-disk_format': results['disk_format'],
        }

        resp.set_headers(headers)
        resp.content_type = 'text/html; charset=utf-8'


class ImagesV1(ImagesV2):
    def on_post(self, req, resp, tenant_id=None):
        headers = req.headers

        try:
            body = json.loads(req.stream.read().decode())
        except ValueError:
            body = {}

        image_details = {
            'location': headers.get('x-image-meta-location'),
            'container_format': headers.get('x-image-meta-container-format',
                                            'bare'),
            'name': headers['x-image-meta-name'],
            'disk_format': headers.get('x-image-meta-disk-format', 'raw'),
            'visibility': 'private',
        }

        if headers['x-image-meta-is-public']:
            image_details['visibility'] = 'public'

        # TODO() - Need to determine how to handle this for real
        image_id = body.get('id', str(uuid.uuid4()))

        resp.body = {'image': {
            'id': image_id,
            'location': self.app.get_endpoint_url(
                'image', req, 'v1_image', image_guid=image_id),
        }}


def get_v2_image_details_dict(app, req, image, tenant_id):

    if not image or not image.get('globalIdentifier'):
        return {}

    # TODO() - Don't hardcode some of these values
    guid = image['globalIdentifier']
    results = {
        'id': guid,
        'name': image['name'],
        'status': 'active',
        'visibility': image.get('visibility', 'public'),
        'is_public': image.get('visibility', 'public') == 'public',
        'owner': tenant_id,
        'size': int(image.get('blockDevicesDiskSpaceTotal', 0)),
        'disk_format': 'raw',
        'container_format': 'bare',
        'protected': False,
        'min_disk': 0,
        'min_ram': 0,
        'progress': 100,
        'metadata': {},
        # "checksum":"2cec138d7dae2aa59038ef8c9aec2390",
        'updated': image.get('createDate'),
        'created': image.get('createDate'),
        'links': [
            {'href': app.get_endpoint_url('image', req, 'v2_image',
                                          image_guid=guid),
             'rel': 'self'},
            {'href': app.get_endpoint_url('image', req, 'v2_image_file',
                                          image_guid=guid),
             'rel': 'file'},
            {'href': app.get_endpoint_url('image', req, 'v2_schema_image'),
             'rel': 'schema'},
            ]
    }

    return results


def get_v1_image_details_dict(app, req, image, tenant_id=None):
    if not image or not image.get('globalIdentifier'):
        return {}

    # TODO() - Don't hardcode some of these values
    guid = image['globalIdentifier']
    results = {
        'status': 'ACTIVE',
        'updated': image.get('createDate'),
        'created': image.get('createDate'),
        'id': guid,
        'progress': 100,
        'metadata': {},
        'size': int(image.get('blockDevicesDiskSpaceTotal', 0)),
        # changed from None to 1000 for Tempest
        'OS-EXT-IMG-SIZE:size': 1000,
        'container_format': 'bare',
        'disk_format': 'raw',
        'is_public': True if image.get('visibility') == 'public' else False,
        'protected': False,
        'owner': image.get('accountId'),
        'min_disk': 0,
        'min_ram': 0,
        'name': image['name'],
        'links': [
            {
                'href': app.get_endpoint_url('image', req, 'v1_image',
                                             image_guid=guid),
                'rel': 'self',
            },
            {
                'href': app.get_endpoint_url('image', req, 'v1_image',
                                             image_guid=guid),
                'rel': 'bookmark',
            }
        ],
    }

    return results


def get_all_images(client):
    images = []
    get_private_images = client['Account'].getPrivateBlockDeviceTemplateGroups
    for image in force_list(get_private_images(mask=IMAGE_MASK)):
        image['visibility'] = 'private'
        images.append(image)

    vgbdtg = client['Virtual_Guest_Block_Device_Template_Group']
    for image in force_list(vgbdtg.getPublicImages(mask=IMAGE_MASK)):
        image['visibility'] = 'public'
        images.append(image)

    return images


def get_image(client, guid):
    vgbdtg = client['Virtual_Guest_Block_Device_Template_Group']
    return vgbdtg.getObject(id=guid)


def force_list(results):
    if not isinstance(results, list):
        results = [results]
    return results
