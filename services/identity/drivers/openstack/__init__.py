from core import api

from .endpoints.index import OpenStackIdentityIndex
from .endpoints.tokens import OpenStackIdentityTokens


api.add_route('/', OpenStackIdentityIndex())
api.add_route('/v2.0/tokens', OpenStackIdentityTokens)