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
    desc =    "Creates a route53 record based on the current instance's \n" \
            + "tag name and specfied hosted zone.\n" \
            + "\n" \
            + "AWS tag name should be in the following format:\n" \
            + "    <subdomain segments>.<product tld>\n" \
            + "    e.g. web1.staging.example.com\n" \
            + "         Subdomain Segments: web1.staging\n" \
            + "         Product TLD:        example.com\n" \
            + "\n" \
            + "The created route53 record name will be in following format:\n" \
            + "    <subdomain segments>.<hosted zone>\n" \
            + "    e.g. web1.staging.r53-pub.example.com\n" \
            + "         Subdomain Segments: web1.staging\n" \
            + "         Hosted Zone:        r53-pub.example.com (must use Route53 DNS servers)\n"
    from argparse import RawTextHelpFormatter
    parser = argparse.ArgumentParser(description=desc, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-p','--product-tld', help='Product TLD will be stripped from Name tag and replaced with Hosted Zone.', required=True, dest='product_tld')
    parser.add_argument('-h','--hosted-zone', help='Hosted Zone (e.g. r53-pub.example.com)', required=True, dest='hosted_zone')
    parser.add_argument('-i','--identity', help='Use instance\'s public or private identity.', required=True, choices=['public', 'private'], dest='identity')
    parser.add_argument('-r','--record-type', help='Type of DNS record to create.', required=True, choices=['A', 'CNAME'], dest='record_type')
    args = vars(parser.parse_args())

    from utils import get_current_instance_id, get_instance, replace_parent_domain
    instance_id = get_current_instance_id()
    instance = get_instance(instance_id)
    tag_name = instance.tags['Name']
    new_domain_name = replace_parent_domain(tag_name, args['product_tld'], args['hosted_zone'])

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
    print "--- %s (register) ---" % datetime.datetime.now()
    print "Instance Tag Name: %s" % tag_name
    print "Record Name:       %s" % new_domain_name
    print "Record Type:       %s" % args['record_type']
    print "Record Value:      %s" % record_value
    update_record(new_domain_name, record_value, args['record_type'], args['hosted_zone'])
