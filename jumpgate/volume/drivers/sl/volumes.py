from SoftLayer import ISCSIManager

class VolumesV2(object):



    def on_get(self, req, resp, tenant_id):
        client = req.env['sl_client']
        volume = ISCSIManager(client)
        params = req
        results = []
        #results = volume_instances
        resp.status = 200
        resp.body = {'volumes': results}
        #resp.body = {'volumes': []}

    def on_post(self, req, resp, tenant_id):
        resp.body = {'volume': {}}


    def list_volumes(self, datacenter=None, size=None):
        """ Lists all the volumes under given account

        :param string datacenter: filter based on datacenter
        :param int size: filter based on size

        :returns: Returns a list of dictionaries represeting the matching volumes.
        """
