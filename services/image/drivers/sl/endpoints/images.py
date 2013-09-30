import json
import falcon

from services.common.error_handling import not_found
from services.image import image_dispatcher as disp


class SLImageV1Image(object):
    __public_images = None
    # This is not a safe place to store private images since this class
    # is only initialized once per app instance
    __private_images = None

    def get_image(self, client, image_guid):
        account = client['Account']

        matching_image = None

        private = self.__private_images

        mask = 'id,accountId,name,globalIdentifier,blockDevices,parentId'

        if not private:
            private = account.getPrivateBlockDeviceTemplateGroups(mask=mask)
            self.__private_images = private

        for image in private:
            if image.get('globalIdentifier') == image_guid:
                matching_image = image
                break

        if not matching_image:
            public = self.__public_images

            if not public:
                vgbd = client['Virtual_Guest_Block_Device_Template_Group']
                public = vgbd.getPublicImages(mask=mask)
                self.__public_images = public

            for image in public:
                if image.get('globalIdentifier') == image_guid:
                    matching_image = image
                    break

        return matching_image

    def on_get(self, req, resp, image_guid):
        client = req.env['sl_client']
        results = self.get_image(client, image_guid)

        if not results:
            return not_found(resp, 'Image could not be found')

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'image': get_image_details_dict(req, results)})

    def on_head(self, req, resp, image_guid):
        client = req.env['sl_client']
        results = get_image_details_dict(
            req, self.get_image(client, image_guid))

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
        resp.body = json.dumps({'image': results})


class SLImageV1Images(object):
    def on_get(self, req, resp):
        client = req.env['sl_client']

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

        # TODO - Figure out why this filter doesn't work
#        for image in image_obj.getPublicImages():
#        images = client['Account'].getBlockDeviceTemplateGroups(filter=filter)
#        print "COUNT: " + str(len(images))
        for image in client['Account'].getBlockDeviceTemplateGroups(**params):
            if not image or image['parentId']:
                continue
            results.append(get_image_details_dict(req, image))

        resp.body = json.dumps({'images':
                                sorted(results,
                                       key=lambda x: x['name'].lower())})


def get_image_details_dict(req, image, tenant_id=None):
    if not image:
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
        'size': image.get('blockDevicesDiskSpaceTotal', 0),
        'OS-EXT-IMG-SIZE:size': None,
        'container_format': 'raw',
        'disk_format': 'raw',
        'is_public': False,
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
