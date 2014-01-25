import logging

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


def handle_softlayer_errors(ex, req, resp, params):
    # Deal with errors detected from the fault code
    for err, msg, factory in FAULT_CODE_ERRORS:
        if ex.faultCode == err:
            return factory(resp,
                           message=msg or ex.faultCode,
                           details=ex.faultString)

    # Deal with errors we can only detect from the fault string
    for err, msg, factory in FAULT_STRING_ERRORS:
        if err in ex.faultString:
            return factory(resp,
                           message=msg or ex.faultCode,
                           details=ex.faultString)

    print(str(ex))
    LOG.exception(ex)
    return compute_fault(resp,
                         message=ex.faultCode,
                         details=ex.faultString)
