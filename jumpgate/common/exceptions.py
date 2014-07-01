import logging

from jumpgate.common import error_handling


LOG = logging.getLogger(__name__)


class ResponseException(Exception):
    error_type = 'error'
    code = 500

    def __init__(self, msg, error_type='error', details=None, code=None):
        Exception.__init__(self, msg)
        self.msg = msg
        self.error_type = error_type or self.error_type
        self.details = details
        self.code = code or self.code

    @staticmethod
    def handle(ex, req, resp, params):
        error_handling.error(resp, ex.error_type, ex.msg,
                             details=ex.details,
                             code=ex.code)


class Unauthorized(ResponseException):
    error_type = 'unauthorized'
    code = 401


class InvalidTokenError(Unauthorized):

    @staticmethod
    def handle(ex, req, resp, params):
        LOG.debug(ex.msg)
        error_handling.error(resp, ex.error_type,
                             "The token is either malformed, expired or not "
                             "valid for the given user/tenant pair",
                             details=ex.details,
                             code=ex.code)
