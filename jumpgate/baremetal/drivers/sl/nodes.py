import SoftLayer


class NodesV1(object):
    def on_get(self, req, resp):
        client = req.env['sl_client']
        hardware = SoftLayer.HardwareManager(client)

        nodes = []
        hw_items = set([
            'id',
            'hostname',
            'domain',
            'hardwareStatus',
            'globalIdentifier',
            'fullyQualifiedDomainName',
            'processorPhysicalCoreAmount',
            'memoryCapacity',
            'primaryBackendIpAddress',
            'primaryIpAddress',
            'datacenter',
        ])
        server_items = set([
            'activeTransaction[id, transactionStatus[friendlyName,name]]',
        ])

        mask = ('[mask[%s],'
                ' mask(SoftLayer_Hardware_Server)[%s]]'
                % (','.join(hw_items), ','.join(server_items)))

        for hw in hardware.list_hardware(mask=mask):
            nodes.append({
                "uuid": hw['id'],
                "instance_uuid": hw['id'],
                # Get the actual power state of every device??? N+1 alert!
                # "power_state": '',
                "provision_state": hw['hardwareStatus']['status'],
            })
        resp.body = {'nodes': nodes}
