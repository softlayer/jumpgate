import logging
import time

from jumpgate.common import hooks

LOG = logging.getLogger(__name__)


@hooks.response_hook(True)
def log_request(req, resp):
    end_time = time.time()
    start_time = req.env.get('sl_timehook_start_time', None)
    if not start_time:
        LOG.error(
            "timelog can only be used along with timedclient request hook")
        return

    timed_client = req.env['sl_client']
    overall = end_time - start_time
    sl_total = 0
    for call, time_stamp, duration in timed_client.get_last_calls():
        LOG.info("[ReqId: %s] %s %s %s",
                 req.env['REQUEST_ID'],
                 call,
                 time_stamp,
                 duration)
        sl_total = sl_total + duration

    LOG.info("[ReqId: %s] %s %s Total: %s, SL Call: %s, Jumpgate: %s",
             req.env['REQUEST_ID'],
             req.method,
             req.path,
             overall,
             sl_total,
             overall - sl_total)
