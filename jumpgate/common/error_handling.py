
def not_implemented(resp, message, details=None, code=501):
    error(resp, 'notImplemented', message, details=details, code=code)


def compute_fault(resp, message, details=None, code=500):
    error(resp, 'computeFault', message, details=details, code=code)


def volume_fault(resp, message, details=None, code=500):
    error(resp, 'volumeFault', message, details=details, code=code)


def bad_request(resp, message, details=None, code=400):
    error(resp, 'badRequest', message, details=details, code=code)


def unauthorized(resp, message, details=None, code=401):
    error(resp, 'unauthorized', message, details=details, code=code)


def not_found(resp, message, details=None, code=404):
    error(resp, 'notFound', message, details=details, code=code)


def duplicate(resp, message, details=None, code=409):
    error(resp, 'duplicate', message, details=details, code=code)


def error(resp, error_type, message, details=None, code=500):
    error_dict = {
        'code': str(code),
        'message': message,
    }
    if details:
        error_dict['details'] = details
    resp.status = code
    resp.body = {error_type: error_dict}
