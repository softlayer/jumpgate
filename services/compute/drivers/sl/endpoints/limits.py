import json
import falcon

from core import api
from services.compute import compute_dispatcher as disp


class SLComputeV2Limits(object):
    def on_get(self, req, resp):
        client = api.config['sl_client']

        account = client['Account'].getObject(
            mask='mask[hourlyVirtualGuestCount]')

        # TODO - This shouldn't be hardcoded
        limits = {
            'absolute': {
                'totalInstancesUsed': account['hourlyVirtualGuestCount'],
                'totalCoresUsed': 0,
                'totalRAMUsed': 0,
                'maxImageMeta': 999999,
                'maxPersonality': 999999,
                'maxPersonalitySize': 999999,
                'maxSecurityGroupRules': 999999,
                'maxSecurityGroups': 999999,
                'maxServerMeta': 999999,
                'maxTotalCores': 999999,
                'maxTotalFloatingIps': 0,
                'maxTotalInstances': 999999,
                'maxTotalKeypairs': 0,
                'maxTotalRAMSize': 999999,
            }
        }

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'limits': limits})
