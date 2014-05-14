import json
import uuid

from SoftLayer.utils import query_filter, NestedDict

from jumpgate.common.utils import lookup
from jumpgate.common.error_handling import not_found, bad_request


class SchemaImageV2(object):
    # TODO - This needs to be updated for our specifications
    image_schema = {
        "name": "image",
        "properties": {
            "architecture": {
                "description": "Operating system architecture as specified in "
                               "http://docs.openstack.org/trunk/"
                               "openstack-compute/admin/content/"
                               "adding-images.html",
                "type": "string"
            },
            "checksum": {
                "description": "md5 hash of image contents. (READ-ONLY)",
                "maxLength": 32,
                "type": "string"
            },
            "container_format": {
                "description": "Format of the container",
                "enum": [
                    "ami",
                    "ari",
                    "aki",
                    "bare",
                    "ovf"
                ],
                "type": "string"
            },
            "created_at": {
                "description": "Date and time of image registration "
                               "(READ-ONLY)",
                "type": "string"
            },
            "direct_url": {
                "description": "URL to access the image file kept in external "
                               "store (READ-ONLY)",
                "type": "string"
            },
            "disk_format": {
                "description": "Format of the disk",
                "enum": [
                    "ami",
                    "ari",
                    "aki",
                    "vhd",
                    "vmdk",
                    "raw",
                    "qcow2",
                    "vdi",
                    "iso"
                ],
                "type": "string"
            },
            "file": {
                "description": "(READ-ONLY)",
                "type": "string"
            },
            "id": {
                "description": "An identifier for the image",
                "pattern": "^([0-9a-fA-F]){8}-"
                           "([0-9a-fA-F]){4}-"
                           "([0-9a-fA-F]){4}-"
                           "([0-9a-fA-F]){4}-"
                           "([0-9a-fA-F]){12}$",
                "type": "string"
            },
            "instance_uuid": {
                "description": "ID of instance used to create this image.",
                "type": "string"
            },
            "kernel_id": {
                "description": "ID of image stored in Glance that should be "
                               "used as the kernel when booting an AMI-style "
                               "image.",
                "pattern": "^([0-9a-fA-F]){8}-"
                           "([0-9a-fA-F]){4}-"
                           "([0-9a-fA-F]){4}-"
                           "([0-9a-fA-F]){4}-"
                           "([0-9a-fA-F]){12}$",
                "type": "string"
            },
            "locations": {
                "description": "A set of URLs to access the image file kept "
                               "in external store",
                "items": {
                    "properties": {
                        "metadata": {
                            "type": "object"
                        },
                        "url": {
                            "maxLength": 255,
                            "type": "string"
                        }
                    },
                    "required": [
                        "url",
                        "metadata"
                    ],
                    "type": "object"
                },
                "type": "array"
            },
            "min_disk": {
                "description": "Amount of disk space (in GB) required to boot "
                               "image.",
                "type": "integer"
            },
            "min_ram": {
                "description": "Amount of ram (in MB) required to boot image.",
                "type": "integer"
            },
            "name": {
                "description": "Descriptive name for the image",
                "maxLength": 255,
                "type": "string"
            },
            "os_distro": {
                "description": "Common name of operating system distribution "
                               "as specified in "
                               "http://docs.openstack.org/trunk/"
                               "openstack-compute/admin/content/"
                               "adding-images.html",
                "type": "string"
            },
            "os_version": {
                "description": "Operating system version as specified by the "
                               "distributor",
                "type": "string"
            },
            "protected": {
                "description": "If true, image will not be deletable.",
                "type": "boolean"
            },
            "ramdisk_id": {
                "description": "ID of image stored in Glance that should be "
                               "used as the ramdisk when booting an AMI-style "
                               "image.",
                "pattern": "^([0-9a-fA-F]){8}-"
                           "([0-9a-fA-F]){4}-"
                           "([0-9a-fA-F]){4}-"
                           "([0-9a-fA-F]){4}-"
                           "([0-9a-fA-F]){12}$",
                "type": "string"
            },
            "schema": {
                "description": "(READ-ONLY)",
                "type": "string"
            },
            "self": {
                "description": "(READ-ONLY)",
                "type": "string"
            },
            "size": {
                "description": "Size of image file in bytes (READ-ONLY)",
                "type": "integer"
            },
            "status": {
                "description": "Status of the image (READ-ONLY)",
                "enum": [
                    "queued",
                    "saving",
                    "active",
                    "killed",
                    "deleted",
                    "pending_delete"
                ],
                "type": "string"
            },
            "tags": {
                "description": "List of strings related to the image",
                "items": {
                    "maxLength": 255,
                    "type": "string"
                },
                "type": "array"
            },
            "updated_at": {
                "description": "Date and time of the last image modification "
                               "(READ-ONLY)",
                "type": "string"
            },
            "visibility": {
                "description": "Scope of image accessibility",
                "enum": [
                    "public",
                    "private"
                ],
                "type": "string"
            }
        },
        "additionalProperties": {
            "type": "string"
        },
        "links": [
            {
                "href": "{self}",
                "rel": "self"
            },
            {
                "href": "{file}",
                "rel": "enclosure"
            },
            {
                "href": "{schema}",
                "rel": "describedby"
            }
        ]
    }

    def on_get(self, req, resp):
        resp.body = self.image_schema


class SchemaImagesV2(SchemaImageV2):
    # TODO - This needs to be updated for our specifications
    def on_get(self, req, resp):
        resp.body = {
            "name": "images",
            "properties": {
                "first": {
                    "type": "string"
                },
                "images": {
                    "items": self.image_schema,
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
    # TODO - This needs to be updated for our specifications
    member_schema = {
        "name": "member",
        "properties": {
            "created_at": {
                "description": "Date and time of image member creation",
                "type": "string"
            },
            "image_id": {
                "description": "An identifier for the image",
                "pattern": "^([0-9a-fA-F]){8}-"
                           "([0-9a-fA-F]){4}-"
                           "([0-9a-fA-F]){4}-"
                           "([0-9a-fA-F]){4}-"
                           "([0-9a-fA-F]){12}$",
                "type": "string"
            },
            "member_id": {
                "description": "An identifier for the image member (tenantId)",
                "type": "string"
            },
            "status": {
                "description": "The status of this image member",
                "enum": [
                    "pending",
                    "accepted",
                    "rejected"
                ],
                "type": "string"
            },
            "updated_at": {
                "description": "Date and time of last modification of image "
                               "member",
                "type": "string"
            },
            "schema": {
                "type": "string"
            }
        }
    }

    def on_get(self, req, resp):
        resp.body = self.member_schema


class SchemaMembersV2(SchemaMemberV2):
    # TODO - This needs to be updated for our specifications
    def on_get(self, req, resp):
        resp.body = {
            "name": "members",
            "properties": {
                "members": self.member_schema,
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
            return not_found(resp, 'Image could not be found')

        client = req.env['sl_client']
        image_obj = SLImages(client)
        results = image_obj.get_image(image_guid)

        if not results:
            return not_found(resp, 'Image could not be found')

        client['Virtual_Guest_Block_Device_Template_Group'].deleteObject(
            id=results['id'])

        resp.status = 204

    def on_post(self, req, resp, tenant_id=None):
        body = json.loads(req.stream.read().decode())

        image_id = body.get('id', str(uuid.uuid4()))
        url = body.get('direct_url')
        osRefCode = body.get('os_version', None)
        if not all([url, osRefCode]):
            raise bad_request(resp, "Swift url and OS code must be given")

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
        tenant_id = tenant_id or lookup(req.env, 'auth', 'tenant_id')

        image_obj = SLImages(client)

        output = []
        limit = None
        if req.get_param('limit'):
            limit = int(req.get_param('limit'))

        marker = req.get_param('marker')

        for visibility, funct in [('public', image_obj.get_public_images),
                                  ('private', image_obj.get_private_images)]:

            if limit == 0:
                break
            results = funct(name=req.get_param('name'),
                            limit=limit,
                            marker=marker)

            if not results:
                continue

            if not isinstance(results, list):
                results = [results]

            for image in results:
                formatted_image = get_v2_image_details_dict(self.app,
                                                            req,
                                                            image,
                                                            tenant_id)

                if formatted_image:
                    formatted_image['visibility'] = visibility
                    output.append(formatted_image)
                    if limit is not None:
                        limit -= 1

        resp.body = {'images': sorted(output,
                                      key=lambda x: x['name'].lower())}


class ImageV1(object):
    def __init__(self, app):
        self.app = app

    def on_delete(self, req, resp, image_guid=None, tenant_id=None):
        if not image_guid:
            return not_found(resp, 'Image could not be found')

        client = req.env['sl_client']
        image_obj = SLImages(client)
        results = image_obj.get_image(image_guid)

        if not results:
            return not_found(resp, 'Image could not be found')

        client['Virtual_Guest_Block_Device_Template_Group'].deleteObject(
            id=results['id'])

        resp.status = 204

    def on_get(self, req, resp, image_guid, tenant_id=None):
        client = req.env['sl_client']
        image_obj = SLImages(client)
        results = image_obj.get_image(image_guid)

        if not results:
            return not_found(resp, 'Image could not be found')

        resp.body = {
            'image': get_v1_image_details_dict(self.app, req, results)}

    def on_head(self, req, resp, image_guid, tenant_id=None):
        client = req.env['sl_client']
        image_obj = SLImages(client)
        results = get_v1_image_details_dict(
            self.app, req, image_obj.get_image(image_guid))

        if not results:
            return not_found(resp, 'Image could not be found')

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

        # TODO - Need to determine how to handle this for real
        image_id = body.get('id', str(uuid.uuid4()))

        resp.body = {'image': {
            'id': image_id,
            'location': self.app.get_endpoint_url(
                'image', req, 'v1_image', image_guid=image_id),
        }}


def get_v2_image_details_dict(app, req, image, tenant_id):

    if not image or not image.get('globalIdentifier'):
        return {}

    # TODO - Don't hardcode some of these values
    results = {
        'id': image['globalIdentifier'],
        'name': image['name'],
        'status': 'active',
        'visibility': image.get('visibility', 'public'),
        'is_public': image.get('visibility', 'public') == 'public',
        'owner': tenant_id,
        'size': int(image.get('blockDevicesDiskSpaceTotal', 0)),
        'disk_format': 'raw',
        'container_format': 'bare',
        'protected': False,
        'properties': {},
        'min_disk': 0,
        'min_ram': 0,
        # "checksum":"2cec138d7dae2aa59038ef8c9aec2390",
        'tags': [],
        'updated': image.get('createDate'),
        'created': image.get('createDate'),
        'self': app.get_endpoint_url('image', req, 'v2_image',
                                     image_guid=image['id']),
        'file': app.get_endpoint_url('image', req, 'v2_image_file',
                                     image_guid=image['id']),
        'schema': app.get_endpoint_url('image', req, 'v2_schema_image'),
    }

    return results


def get_v1_image_details_dict(app, req, image, tenant_id=None):
    if not image or not image.get('globalIdentifier'):
        return {}

    # TODO - Don't hardcode some of these values
    results = {
        'status': 'ACTIVE',
        'updated': image.get('createDate'),
        'created': image.get('createDate'),
        'id': image['globalIdentifier'],
        'progress': 100,
        'metaData': None,
        'size': int(image.get('blockDevicesDiskSpaceTotal', 0)),
        'OS-EXT-IMG-SIZE:size': None,
        'container_format': 'bare',
        'disk_format': 'raw',
        'properties': {},
        'is_public': True if image.get('visibility') == 'public' else False,
        'protected': False,
        'owner': image.get('accountId'),
        'min_disk': 0,
        'min_ram': 0,
        'name': image['name'],
        'links': [
            {
                'href': app.get_endpoint_url('image', req, 'v1_image',
                                             image_guid=image['id']),
                'rel': 'self',
            },
            {
                'href': app.get_endpoint_url('image', req, 'v1_image',
                                             image_guid=image['id']),
                'rel': 'bookmark',
            }
        ],
        'properties': {

        },
    }

    return results


class SLImages(object):
    image_mask = ('id,accountId,name,globalIdentifier,blockDevices,parentId,'
                  'createDate,blockDevicesDiskSpaceTotal')

    def __init__(self, client):
        self.client = client

    def get_image(self, guid):
        matching_image = None

        matching_image = self.get_public_images(guid=guid, limit=1)
        if matching_image:
            matching_image['visibility'] = 'public'
            return matching_image

        matching_image = self.get_private_images(guid=guid, limit=1)
        if matching_image:
            matching_image['visibility'] = 'private'
            return matching_image

        return matching_image

    def get_private_images(self, guid=None, name=None, limit=None,
                           marker=None):
        _filter = NestedDict()
        if name:
            _filter['privateBlockDeviceTemplateGroups']['name'] = \
                query_filter(name)

        if marker is not None:
            _filter['privateBlockDeviceTemplateGroups']['globalIdentifier'] = \
                query_filter('> %s' % marker)

        if guid:
            _filter['privateBlockDeviceTemplateGroups'] = {
                'globalIdentifier': query_filter(guid)}

        params = {}
        params['mask'] = self.image_mask

        if _filter:
            params['filter'] = _filter.to_dict()

        if limit:
            params['limit'] = limit

        account = self.client['Account']
        return account.getPrivateBlockDeviceTemplateGroups(**params)

    def get_public_images(self, guid=None, name=None, limit=None, marker=None):
        _filter = NestedDict()
        if name:
            _filter['name'] = query_filter(name)

        if guid:
            _filter['globalIdentifier'] = query_filter(guid)

        if marker is not None:
            _filter['globalIdentifier'] = query_filter('> %s' % marker)

        params = {}
        params['mask'] = self.image_mask

        if _filter:
            params['filter'] = _filter.to_dict()

        if limit:
            params['limit'] = limit

        vgbdtg = self.client['Virtual_Guest_Block_Device_Template_Group']
        return vgbdtg.getPublicImages(**params)
