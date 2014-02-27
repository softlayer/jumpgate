from jumpgate.common.sl.errors import handle_softlayer_errors
from SoftLayer import SoftLayerAPIError


def add_hooks(app):
    app.add_error_handler(SoftLayerAPIError, handle_softlayer_errors)
