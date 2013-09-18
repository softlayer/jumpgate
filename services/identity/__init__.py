from services.common.dispatcher import Dispatcher
from core import api

identity_dispatcher = Dispatcher(api)

identity_dispatcher.add_endpoint('index_v3', '/v3')
identity_dispatcher.add_endpoint('tokens_v3', '/v3/tokens')
