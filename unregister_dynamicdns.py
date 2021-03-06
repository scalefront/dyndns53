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
        if record.type != record_type or record.name != record_name.replace('*', '\\052'):
            continue
        change = records.add_change(action='DELETE',
                                    name=record.name,
                                    type=record.type)
        change.__dict__.update(record.__dict__)

    if change is not None:
        records.commit()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Deletes a route53 record created by dynamicdns.register_dynamicdns.")
    parser.add_argument('-p','--product-tld', help='Product TLD will be stripped from Name tag and replaced with Hosted Zone.', required=True, dest='product_tld')
    parser.add_argument('-z','--hosted-zone', help='Hosted Zone (e.g. r53-pub.example.com)', required=True, dest='hosted_zone')
    parser.add_argument('-r','--record-type', help='Type of DNS record to delete.', required=True, choices=['A', 'CNAME'], dest='record_type')
    parser.add_argument('-s','--subdomain', help='Prefix a subdomain onto the record.', required=False, dest='subdomain')
    parser.add_argument('-d','--dry-run', help='Don\'t actually unregister the domain.', action='store_true', default=False, dest='dry_run')
    args = vars(parser.parse_args())

    from domain_name import generate_domain_name
    domain_name = generate_domain_name(args['product_tld'], args['hosted_zone'], args['subdomain'], end_with_period=True)

    import datetime
    print "--- %s (unregister) ---" % datetime.datetime.now()
    print "Record Name:       %s" % domain_name
    print "Record Type:       %s" % args['record_type']
    if args['dry_run']:
        print "--- Dry run only ---"
    else:
        delete_record(domain_name, args['record_type'], args['hosted_zone'])
