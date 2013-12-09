from functools import wraps
import logging

from SoftLayer import SoftLayerAPIError, TransportError

from jumpgate.common.error_handling import (
    bad_request, not_found, compute_fault, unauthorized)

LOG = logging.getLogger(__name__)

FAULT_CODE_ERRORS = [
    ('SoftLayer_Exception_MissingCreationProperty', None, bad_request),
    ('SoftLayer_Exception_InvalidValue', None, bad_request),
    ('SoftLayer_Exception_InvalidDataLength', None, bad_request),
    ('SoftLayer_Exception_ObjectNotFound', None, not_found),
    ('SoftLayer_Exception_NotFound', None, not_found),
    ('SoftLayer_Exception_InvalidLegacyToken', 'Invalid Credentials',
     unauthorized)
]

FAULT_STRING_ERRORS = [
    ('must be alphanumeric strings', 'Invalid hostname', bad_request),
    ('Invalid API token', 'Invalid credentials', unauthorized),
]


def convert_errors(handler):

    @wraps(handler)
    def funct(*args, **kwargs):
        resp = args[2]
        try:
            return handler(*args, **kwargs)
        except SoftLayerAPIError as e:
            # Deal with errors detected from the fault code
            for err, msg, factory in FAULT_CODE_ERRORS:
                if e.faultCode == err:
                    return factory(resp,
                                   message=msg or e.faultCode,
                                   details=e.faultString)

            # Deal with errors we can only detect from the fault string
            for err, msg, factory in FAULT_STRING_ERRORS:
                if err in e.faultString:
                    return factory(resp,
                                   message=msg or e.faultCode,
                                   details=e.faultString)

            LOG.exception(e)
            return compute_fault(resp,
                                 message=e.faultCode,
                                 details=e.faultString)
        except TransportError as e:
            LOG.exception(e)
            return compute_fault(resp,
                                 message='Service Unavailable',
                                 details='Service Unavailable')

    return funct
