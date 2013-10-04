import json
import falcon
from services.common.nested_dict import lookup
from services.common.error_handling import bad_request
from SoftLayer import SoftLayerAPIError


class SLComputeV2ServerMetadata(object):
    def on_get(self, req, resp, tenant_id, server_id):
        client = req.env['sl_client']
        results = client['Virtual_Guest'].getObject(id=server_id,
                                                    mask='id, userData')
        resp.body = {'metadata': decode_metadata(results.get('userData'))}

    def on_post(self, req, resp, tenant_id, server_id):
        body = json.loads(req.stream.read().decode())
        print("SLComputeV2ServerMetadata.on_post()", body)
        client = req.env['sl_client']
        results = client['Virtual_Guest'].getObject(id=server_id,
                                                    mask='id, userData')
        metadata = lookup(body, 'metadata')
        current_metadata = decode_metadata(results.get('userData'))
        for key, value in metadata.items():
            current_metadata[key] = value

        try:
            client['Virtual_Guest'].setUserMetadata(
                [encode_metadata(current_metadata)], id=server_id)
        except SoftLayerAPIError as e:
            if e.faultCode == 'SoftLayer_Exception_InvalidDataLength':
                return bad_request(
                    resp, code=falcon.HTTP_413, message="Metadata too large")

        resp.body = {'metadata': current_metadata}

    def on_put(self, req, resp, tenant_id, server_id):
        body = json.loads(req.stream.read().decode())
        print("SLComputeV2ServerMetadata.on_put()", body)
        client = req.env['sl_client']
        metadata = lookup(body, 'metadata')
        try:
            client['Virtual_Guest'].setUserMetadata(encode_metadata(metadata),
                                                    id=server_id)
        except SoftLayerAPIError as e:
            if e.faultCode == 'SoftLayer_Exception_InvalidDataLength':
                return bad_request(
                    resp, code=falcon.HTTP_413, message="Metadata too large")

        resp.body = {'metadata': metadata}


class SLComputeV2ServerMetadataKey(object):
    def on_put(self, req, resp, tenant_id, server_id, key):
        body = json.loads(req.stream.read().decode())
        print("SLComputeV2ServerMetadataKey.on_put()", body)
        client = req.env['sl_client']
        results = client['Virtual_Guest'].getObject(id=server_id,
                                                    mask='id, userData')
        metadata = lookup(body, 'meta')
        current_metadata = decode_metadata(results.get('userData'))
        for key, value in metadata.items():
            current_metadata[key] = value

        try:
            client['Virtual_Guest'].setUserMetadata(
                [encode_metadata(current_metadata)], id=server_id)
        except SoftLayerAPIError as e:
            if e.faultCode == 'SoftLayer_Exception_InvalidDataLength':
                return bad_request(
                    resp, code=falcon.HTTP_413, message="Metadata too large")

        resp.body = {'meta': current_metadata}

    def on_get(self, req, resp, tenant_id, server_id, key):
        client = req.env['sl_client']
        results = client['Virtual_Guest'].getObject(id=server_id,
                                                    mask='id, userData')
        resp.body = {'meta': decode_metadata(results.get('userData'))}

    def on_delete(self, req, resp, tenant_id, server_id, key):
        client = req.env['sl_client']
        results = client['Virtual_Guest'].getObject(id=server_id,
                                                    mask='id, userData')
        current_metadata = decode_metadata(results.get('userData'))
        try:
            del(current_metadata[key])
        except KeyError:
            # 404 Error?
            pass

        client['Virtual_Guest'].setUserMetadata(
            [encode_metadata(current_metadata)], id=server_id)

        resp.status = falcon.HTTP_204
        resp.body = {'metadata': current_metadata}


def decode_metadata(sl_metadata):
    metadata = {}
    if sl_metadata:
        try:
            metadata = json.loads(sl_metadata[0]['value'])
        except ValueError:
            pass
    return metadata


def encode_metadata(metadata):
    return json.dumps(metadata)
