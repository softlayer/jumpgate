import logging

from jumpgate.common import error_handling as e

LOG = logging.getLogger(__name__)

FAULT_CODE_ERRORS = [
    ('SoftLayer_Exception_MissingCreationProperty', None, e.bad_request),
    ('SoftLayer_Exception_InvalidValue', None, e.bad_request),
    ('SoftLayer_Exception_InvalidDataLength', None, e.bad_request),
    ('SoftLayer_Exception_ObjectNotFound', None, e.not_found),
    ('SoftLayer_Exception_NotFound', None, e.not_found),
    ('SoftLayer_Exception_InvalidLegacyToken',
     'Invalid Credentials', e.unauthorized)
]

FAULT_STRING_ERRORS = [
    ('must be alphanumeric strings', 'Invalid hostname', e.bad_request),
    ('Invalid API token', 'Invalid credentials', e.unauthorized),
    ('No valid authentication headers found',
     'Invalid credentials', e.unauthorized)
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

    LOG.exception('Unexpected SoftLayer Error')
    return e.compute_fault(resp,
                           message=ex.faultCode,
                           details=ex.faultString)
