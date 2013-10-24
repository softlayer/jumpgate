import json
import falcon
import uuid

from SoftLayer.utils import query_filter

from babelfish.common.error_handling import not_found
from babelfish.image import image_dispatcher as disp


class SchemaImagesV2(object):
    # TODO - This needs to be updated for our specifications
    def on_get(self, req, resp):
        resp.body = {
            "name": "images",
            "properties": {
                "first": {
                    "type": "string"
                },
                "images": {
                    "items": {
                        "name": "image",
                        "properties": {
                            "architecture": {
                                "description": "Operating system architecture as specified in http://docs.openstack.org/trunk/openstack-compute/admin/content/adding-images.html",
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
                                "description": "Date and time of image registration (READ-ONLY)",
                                "type": "string"
                            },
                            "direct_url": {
                                "description": "URL to access the image file kept in external store (READ-ONLY)",
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
                                "pattern": "^([0-9a-fA-F]){8}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){12}$",
                                "type": "string"
                            },
                            "instance_uuid": {
                                "description": "ID of instance used to create this image.",
                                "type": "string"
                            },
                            "kernel_id": {
                                "description": "ID of image stored in Glance that should be used as the kernel when booting an AMI-style image.",
                                "pattern": "^([0-9a-fA-F]){8}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){12}$",
                                "type": "string"
                            },
                            "locations": {
                                "description": "A set of URLs to access the image file kept in external store",
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
                                "description": "Amount of disk space (in GB) required to boot image.",
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
                                "description": "Common name of operating system distribution as specified in http://docs.openstack.org/trunk/openstack-compute/admin/content/adding-images.html",
                                "type": "string"
                            },
                            "os_version": {
                                "description": "Operating system version as specified by the distributor",
                                "type": "string"
                            },
                            "protected": {
                                "description": "If true, image will not be deletable.",
                                "type": "boolean"
                            },
                            "ramdisk_id": {
                                "description": "ID of image stored in Glance that should be used as the ramdisk when booting an AMI-style image.",
                                "pattern": "^([0-9a-fA-F]){8}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){12}$",
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
                                "description": "Date and time of the last image modification (READ-ONLY)",
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
                    },
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


class SchemaImageV2(object):
    # TODO - This needs to be updated for our specifications
    def on_get(self, req, resp):
        resp.body = {
            "name": "image",
            "properties": {
                "architecture": {
                    "description": "Operating system architecture as specified in http://docs.openstack.org/trunk/openstack-compute/admin/content/adding-images.html",
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
                    "description": "Date and time of image registration (READ-ONLY)",
                    "type": "string"
                },
                "direct_url": {
                    "description": "URL to access the image file kept in external store (READ-ONLY)",
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
                    "pattern": "^([0-9a-fA-F]){8}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){12}$",
                    "type": "string"
                },
                "instance_uuid": {
                    "description": "ID of instance used to create this image.",
                    "type": "string"
                },
                "kernel_id": {
                    "description": "ID of image stored in Glance that should be used as the kernel when booting an AMI-style image.",
                    "pattern": "^([0-9a-fA-F]){8}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){12}$",
                    "type": "string"
                },
                "locations": {
                    "description": "A set of URLs to access the image file kept in external store",
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
                    "description": "Amount of disk space (in GB) required to boot image.",
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
                    "description": "Common name of operating system distribution as specified in http://docs.openstack.org/trunk/openstack-compute/admin/content/adding-images.html",
                    "type": "string"
                },
                "os_version": {
                    "description": "Operating system version as specified by the distributor",
                    "type": "string"
                },
                "protected": {
                    "description": "If true, image will not be deletable.",
                    "type": "boolean"
                },
                "ramdisk_id": {
                    "description": "ID of image stored in Glance that should be used as the ramdisk when booting an AMI-style image.",
                    "pattern": "^([0-9a-fA-F]){8}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){12}$",
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
                    "description": "Date and time of the last image modification (READ-ONLY)",
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


class ImagesV2(object):
    def on_delete(self, req, resp, image_guid=None, tenant_id=None):
        if not image_guid:
            return not_found(resp, 'Image could not be found')

        client = req.env['sl_client']
        image_obj = SLImages(client)
        results = image_obj.get_image(image_guid)

        if not results:
            return not_found(resp, 'Image could not be found')

        # TODO - What should this do?
        resp.status = falcon.HTTP_204

    def on_post(self, req, resp, tenant_id=None):
        body = json.loads(req.stream.read().decode())

        # TODO - Need to determine how to handle this for real
        id = body.get('id', str(uuid.uuid4()))

        resp.body = {
            'id': id,
            'name': body['name'],
            'status': 'queued',
            'visibility': body.get('visibility', 'public'),
            'tags': [],
            'created_at': '2012-08-11T17:15:52Z',
            'updated_at': '2012-08-11T17:15:52Z',
            'self': disp.get_endpoint_url(req, 'v2_image', image_guid=id),
            'file': disp.get_endpoint_url(req, 'v2_image_file', image_guid=id),
            'schema': disp.get_endpoint_url(req, 'v2_schema_image'),
        }

    def on_get(self, req, resp, tenant_id=None):
        client = req.env['sl_client']

        filter = {}

        if req.get_param('name'):
            query = query_filter(req.get_param('name'))
            if 'blockDeviceTemplateGroups' not in filter:
                filter['blockDeviceTemplateGroups'] = {}
            filter['blockDeviceTemplateGroups']['name'] = query

        # filter = {
        #     'blockDeviceTemplateGroups':
        #     {
        #         'parentId': {
        #             'operation': 'is_null',
        #         }
        #     }
        # }
        results = []

        params = {}
        params['mask'] = get_image_mask()

        if filter:
            params['filter'] = filter

        if req.get_param('limit'):
            params['limit'] = req.get_param('limit')

        results = client['Account'].getBlockDeviceTemplateGroups(**params)

        if not results:
            resp.body = {}
            return

        if not isinstance(results, list):
            results = [results]

        output = []
        for image in results:
            if not image:  # or 'parentId' not in image:
                continue
            formatted_image = get_v2_image_details_dict(req, image)

            if formatted_image:
                formatted_image['visibility'] = 'private'
                output.append(formatted_image)

        resp.body = {'images': sorted(output,
                                      key=lambda x: x['name'].lower())}


class ImageV1(object):
    def on_delete(self, req, resp, image_guid=None, tenant_id=None):
        if not image_guid:
            return not_found(resp, 'Image could not be found')

        client = req.env['sl_client']
        image_obj = SLImages(client)
        results = image_obj.get_image(image_guid)

        if not results:
            return not_found(resp, 'Image could not be found')

        # TODO - What should this do?
        resp.status = falcon.HTTP_204

    def on_get(self, req, resp, image_guid, tenant_id=None):
        client = req.env['sl_client']
        image_obj = SLImages(client)
        results = image_obj.get_image(image_guid)

        if not results:
            return not_found(resp, 'Image could not be found')

        resp.status = falcon.HTTP_200
        resp.body = {'image': get_v1_image_details_dict(req, results)}

    def on_head(self, req, resp, image_guid, tenant_id=None):
        client = req.env['sl_client']
        image_obj = SLImages(client)
        results = get_v1_image_details_dict(
            req, image_obj.get_image(image_guid))

        if not results:
            return not_found(resp, 'Image could not be found')

        headers = {
            'x-image-meta-id': image_guid,
            'x-image-meta-status': results['status'].lower(),
            'x-image-meta-owner': 'Need tenant ID here',
            'x-image-meta-name': results['name'],
            'x-image-meta-container_format': results['container_format'],
            'x-image-meta-created_at': results['created'],
            'x-image-meta-min_ram': results['minRam'],
            'x-image-meta-updated_at': results['updated'],
            'location': disp.get_endpoint_url(req, 'v1_image',
                                              image_guid=image_guid),
            'x-image-meta-deleted': False,
            'x-image-meta-protected': results['protected'],
            'x-image-meta-min_disk': results['minDisk'],
            'x-image-meta-size': results['size'],
            'x-image-meta-is_public': results['is_public'],
            'x-image-meta-disk_format': results['disk_format'],
        }

        resp.status = falcon.HTTP_200
        resp.set_headers(headers)


class ImagesV1(object):
    def on_get(self, req, resp, tenant_id=None):
        client = req.env['sl_client']
        image_obj = SLImages(client)

        results = []

        for image in image_obj.get_public_images():
            if not image:  # or 'parentId' not in image:
                continue
            image['visibility'] = 'public'
            formatted_image = get_v1_image_details_dict(req, image)

            if formatted_image:
                results.append(formatted_image)

        for image in image_obj.get_private_images():
            if not image:  # or 'parentId' not in image:
                continue
            image['visibility'] = 'private'
            formatted_image = get_v1_image_details_dict(req, image)

            if formatted_image:
                results.append(formatted_image)

        resp.body = {'images': sorted(results,
                                      key=lambda x: x['name'].lower())}

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
        id = body.get('id', str(uuid.uuid4()))

        resp.body = {'image': {
            'id': id,
            'location': disp.get_endpoint_url(req, 'v1_image', image_guid=id),
        }}


def get_v2_image_details_dict(req, image, tenant_id=None):
    if not image or not image.get('globalIdentifier'):
        return {}

    # TODO - Don't hardcode some of these values
    results = {
        'id': image['globalIdentifier'],
        'name': image['name'],
        'status': 'active',
        'visibility': image.get('visibility', 'public'),
        'size': int(image.get('blockDevicesDiskSpaceTotal', 0)),
#        "checksum":"2cec138d7dae2aa59038ef8c9aec2390",
        'tags': [],
        'updated': image.get('createDate'),
        'created': image.get('createDate'),
        'self': disp.get_endpoint_url(req, 'v2_image', image_guid=image['id']),
        'file': disp.get_endpoint_url(req, 'v2_image_file',
                                      image_guid=image['id']),
        'schema': disp.get_endpoint_url(req, 'v2_schema_image'),
    }

    return results


def get_v1_image_details_dict(req, image, tenant_id=None):
    if not image or not image.get('globalIdentifier'):
        return {}

    # TODO - Don't hardcode some of these values
    results = {
        'status': 'ACTIVE',
        'updated': image.get('createDate'),
        'created': image.get('createDate'),
        'id': image['globalIdentifier'],
        'minDisk': 0,
        'progress': 100,
        'minRam': 0,
        'metaData': None,
        'size': int(image.get('blockDevicesDiskSpaceTotal', 0)),
        'OS-EXT-IMG-SIZE:size': None,
        'container_format': 'raw',
        'disk_format': 'raw',
        'is_public': True if image.get('visibility') == 'public' else False,
        'protected': False,
        'owner': tenant_id,
        'name': image['name'],
        'links': [
            {
                'href': disp.get_endpoint_url(req, 'v1_image',
                                              image_guid=image['id']),
                'rel': 'self',
            },
            {
                'href': disp.get_endpoint_url(req, 'v1_image',
                                              image_guid=image['id']),
                'rel': 'bookmark',
            }
        ],
        'properties': {

        },
    }

    return results


def get_image_mask():
    mask = [
        'blockDevicesDiskSpaceTotal',
        'globalIdentifier',
    ]

    return 'mask[%s]' % ','.join(mask)


class SLImages(object):
    __public_images = None
#    __private_images = None

    def __init__(self, client):
        self.client = client

    def get_image(self, image_guid=None, name=None, most_recent=False):
        matching_image = None

        private = self.get_private_images()
        time = ''

        if image_guid:
            key = 'globalIdentifier'
            value = image_guid
        else:
            key = 'name'
            value = name

        for image in private:
            if image.get(key) == value:
                if not most_recent or image['createDate'] > time:
                    matching_image = image
                    matching_image['visibility'] = 'private'
                    time = image['createDate']
                    if not most_recent:
                        break

        if not matching_image:
            public = self.get_public_images()

            for image in public:
                if image.get(key) == value:
                    if not most_recent or image['createDate'] > time:
                        matching_image = image
                        matching_image['visibility'] = 'public'
                        time = image['createDate']
                        if not most_recent:
                            break

        return matching_image

    def get_private_images(self):
#        private = self.__private_images

        private = None

        if not private:
            mask = 'id,accountId,name,globalIdentifier,blockDevices' + \
                   ',parentId,createDate'

            account = self.client['Account']
            private = account.getPrivateBlockDeviceTemplateGroups(mask=mask)
 #           self.__private_images = private

        return private

    def get_public_images(self):
        public = self.__public_images

        if not public:
            mask = 'id,accountId,name,globalIdentifier,blockDevices' + \
                   ',parentId,createDate'

            vgbd = self.client['Virtual_Guest_Block_Device_Template_Group']
            public = vgbd.getPublicImages(mask=mask)
            self.__public_images = public

        return public
