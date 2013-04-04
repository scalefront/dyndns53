#!/usr/bin/env python

def delete_record(record_name, record_type, zone_domain_name):
    from boto.route53.connection import Route53Connection
    conn = Route53Connection()
    zone = conn.get_hosted_zone_by_name(zone_domain_name)
    if zone is None:
        raise ValueError("Domain name \"%s\" not found in zones." % zone_domain_name)

    records = conn.get_all_rrsets(hosted_zone_id=zone.Id.split('/')[-1])
    # Remove old records if they exist
    change = None
    for record in records:
        if record.type != record_type or record.name != record_name:
            continue
        change = records.add_change(action='DELETE',
                                    name=record.name,
                                    type=record.type)
        change.__dict__.update(record.__dict__)

    if change is not None:
        records.commit()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Creates a route53 A-record based on the current instance's tag name.")
    parser.add_argument('-t','--truncate-name', help='Remove matching text from rhs of instance Name tag value.', required=True, dest='truncate_name')
    parser.add_argument('-z','--zone-domain-name', help='Zone Domain Name (e.g. ec2-pub.website.com)', required=True, dest='zone_domain_name')
    parser.add_argument('-r','--record-type', help='Type of DNS record to create.', required=True, choices=['A', 'CNAME'], dest='record_type')
    args = vars(parser.parse_args())

    from utils import get_current_instance_id, get_instance, replace_parent_domain
    instance_id = get_current_instance_id()
    instance = get_instance(instance_id)
    tag_name = instance.tags['Name']
    new_domain_name = replace_parent_domain(tag_name, args['truncate_name'], args['zone_domain_name'])

    import datetime
    print "--- %s (unregister) ---" % datetime.datetime.now()
    print "Instance Tag Name: %s" % tag_name
    print "Record Name:       %s" % new_domain_name
    print "Record Type:       %s" % args['record_type']
    delete_record(new_domain_name, args['record_type'], args['zone_domain_name'])
