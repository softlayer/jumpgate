import json

from six.moves.urllib import parse  # pylint: disable=E0611
import SoftLayer

from jumpgate.common import utils


class DNSDomainsV2(object):
    def on_get(self, req, resp, tenant_id):
        client = req.env['sl_client']
        mgr = SoftLayer.DNSManager(client)

        results = []

        for zone in mgr.list_zones():
            results.append({
                'project': None,
                'scope': 'public',
                'domain': zone['name'],
                'availability_zone': None,
            })

        resp.body = {'domain_entries': results}


class DNSDomainEntryV2(object):
    def on_delete(self, req, resp, tenant_id, domain, entry):
        client = req.env['sl_client']
        mgr = SoftLayer.DNSManager(client)

        domain = parse.unquote_plus(domain)

        zone_id = mgr._get_zone_id_from_name(domain)[0]

        record = mgr.get_records(zone_id, host=entry)[0]

        mgr.delete_record(record['id'])

        resp.status = 204

    def on_get(self, req, resp, tenant_id, domain, entry=None):
        client = req.env['sl_client']
        mgr = SoftLayer.DNSManager(client)

        domain = parse.unquote_plus(domain)

        zone_id = mgr._get_zone_id_from_name(domain)[0]

        if entry:
            record = mgr.get_records(zone_id, host=entry)[0]

        result = get_dns_entry_dict(domain, record['host'], record['data'],
                                    record['type'], entry_id=record['id'])

        resp.body = {'dns_entry': result}

    def on_put(self, req, resp, tenant_id, domain, entry):
        client = req.env['sl_client']
        mgr = SoftLayer.DNSManager(client)

        body = json.loads(req.stream.read().decode())
        ip = utils.lookup(body, 'dns_entry', 'ip')
        record_type = utils.lookup(body, 'dns_entry', 'type')
        if not record_type:
            record_type = 'A'

        domain = parse.unquote_plus(domain)
        zone_id = mgr._get_zone_id_from_name(domain)[0]
        mgr.create_record(zone_id=zone_id, record=entry,
                          record_type=record_type, data=ip)
        new_record = mgr.get_records(zone_id, host=entry)[0]
        result = get_dns_entry_dict(domain, entry, ip, record_type,
                                    entry_id=new_record['id'])

        resp.body = {'dns_entry': result}


def get_dns_entry_dict(domain, name, ip, entry_type, entry_id=None):
    return {
        'ip': ip,
        'domain': domain,
        'type': entry_type,
        'id': entry_id,
        'name': name,
    }
