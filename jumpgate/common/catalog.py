def build_catalog(services):
    catalog = []

    for service_type, service in services.items():
        d = {
            'type': service_type,
            'name': service.get('name', 'Unknown'),
            'endpoints': [{
                'region': service.get('region', 'RegionOne'),
                'publicURL': service.get('publicURL'),
                'privateURL': service.get('privateURL'),
                'adminURL': service.get('adminURL'),
            }],
            'endpoint_links': [],
        }
        catalog.append(d)

    return catalog


def parse_templates(template_lines):
    o = {}
    for line in template_lines:
        if ' = ' not in line:
            continue

        k, v = line.strip().split(' = ')
        if not k.startswith('catalog.'):
            continue

        parts = k.split('.')

        region, service, key = parts[1:4]

        region_ref = o.get(region, {})
        service_ref = region_ref.get(service, {})
        service_ref[key] = v

        region_ref[service] = service_ref
        o[region] = region_ref

    return o
