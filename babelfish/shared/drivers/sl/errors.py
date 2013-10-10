from functools import wraps
import sys
import traceback

from SoftLayer import SoftLayerAPIError

from babelfish.common.error_handling import (
    bad_request, not_found, compute_fault, unauthorized)


def convert_errors(handler):

    @wraps(handler)
    def funct(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except SoftLayerAPIError as e:
            cls, req, resp = args[:3]
            if e.faultCode == 'SoftLayer_Exception_InvalidValue':
                return bad_request(resp, message=e.faultCode,
                                   details=e.faultString)
            elif e.faultCode == 'SoftLayer_Exception_InvalidDataLength':
                return bad_request(
                    resp, message=e.faultCode, details=e.faultString)
            elif e.faultCode == 'SoftLayer_Exception_ObjectNotFound':
                return not_found(resp, 'Object could not be found')
            elif e.faultCode == 'SoftLayer_Exception_NotFound':
                return not_found(resp, 'Object could not be found')
            elif e.faultCode == 'SoftLayer_Exception_MissingCreationProperty':
                return bad_request(
                    resp, message=e.faultCode, details=e.faultString)
            elif 'must be alphanumeric strings' in e.faultString:
                return bad_request(
                    resp, message='Invalid hostname', details=e.faultString)
            elif e.faultCode == 'SoftLayer_Exception_InvalidLegacyToken':
                return unauthorized(resp,
                                    message='Invalid Credentials',
                                    details=e.faultString)
            elif 'Invalid API token' in e.faultString:
                return unauthorized(resp,
                                    message='Invalid Credentials',
                                    details=e.faultString)

            traceback.print_exc(file=sys.stderr)
            return compute_fault(
                resp, message=e.faultCode, details=e.faultString)

    return funct
