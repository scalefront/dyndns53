#!/usr/bin/env python

def update_record(record_name, record_value, record_type, zone_domain_name):
    from boto.route53.connection import Route53Connection
    conn = Route53Connection()
    zone = conn.get_hosted_zone_by_name(zone_domain_name)
    if zone is None:
        raise ValueError("Domain name \"%s\" not found in zones." % zone_domain_name)

    records = conn.get_all_rrsets(hosted_zone_id=zone.Id.split('/')[-1])
    # Remove old records if they exist
    for record in records:
        if record.type != record_type or record.name != record_name:
            continue
        change = records.add_change(action='DELETE',
                                    name=record.name,
                                    type=record.type)
        change.__dict__.update(record.__dict__)
    # Create new record with current value
    change = records.add_change(action='CREATE',
                                name=record_name,
                                type=record_type,
                                ttl=60)
    change.add_value(record_value)
    records.commit()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Creates a route53 A-record based on the current instance's tag name.")
    parser.add_argument('-t','--truncate-name', help='Remove matching text from rhs of instance Name tag value.', required=True, dest='truncate_name')
    parser.add_argument('-z','--zone-domain-name', help='Zone Domain Name (e.g. ec2-pub.website.com)', required=True, dest='zone_domain_name')
    parser.add_argument('-i','--identity', help='Use instances public or private identity.', required=True, choices=['public', 'private'], dest='identity')
    parser.add_argument('-r','--record-type', help='Type of DNS record to create.', required=True, choices=['A', 'CNAME'], dest='record_type')
    args = vars(parser.parse_args())

    from utils import get_current_instance_id, get_instance, replace_parent_domain
    instance_id = get_current_instance_id()
    instance = get_instance(instance_id)
    tag_name = instance.tags['Name']
    new_domain_name = replace_parent_domain(tag_name, args['truncate_name'], args['zone_domain_name'])

    # Determine the appropriate record value (pub/priv ip/dns_name)
    if args['record_type'] == 'A':
        if args['identity'] == 'private':
            record_value = instance.private_ip_address
        else:
            record_value = instance.ip_address
    else:
        if args['identity'] == 'private':
            record_value = instance.private_dns_name
        else:
            record_value = instance.public_dns_name

    import datetime
    print "--- %s ---" % datetime.datetime.now()
    print "Instance Tag Name: %s" % tag_name
    print "Record Name:       %s" % new_domain_name
    print "Record Type:       %s" % args['record_type']
    print "Record Value:      %s" % record_value
    update_record(new_domain_name, record_value, args['record_type'], args['zone_domain_name'])
