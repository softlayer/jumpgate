from jumpgate.common.dispatcher import Dispatcher


def get_dispatcher():
    disp = Dispatcher()

    disp.add_endpoint('main_index', '/')

    disp.add_endpoint('v3_index', '/v3')
    disp.add_endpoint('v2_index', '/v2')
    return disp
