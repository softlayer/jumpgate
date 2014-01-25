

class ResponseException(Exception):
    error_type = 'error'
    code = 500

    def __init__(self, msg, error_type='error', details=None, code=None):
        Exception.__init__(self, msg)
        self.msg = msg
        self.error_type = error_type or self.error_type
        self.details = details
        self.code = code or self.code


class Unauthorized(ResponseException):
    error_type = 'unauthorized'
    code = 401
