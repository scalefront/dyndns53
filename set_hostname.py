#!/usr/bin/env python

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Prints a hostname based on the current AWS instance's \"Name\" tag \
            and specified hosted zone.")
    parser.add_argument('-p','--product-tld', help='Product TLD will be stripped from Name tag and replaced with Hosted Zone.', required=True, dest='product_tld')
    parser.add_argument('-z','--hosted-zone', help='Hosted Zone (e.g. r53-pub.example.com)', required=True, dest='hosted_zone')
    args = vars(parser.parse_args())

    from utils import get_current_instance_id, get_instance, replace_parent_domain
    instance_id = get_current_instance_id()
    instance = get_instance(instance_id)
    tag_name = instance.tags['Name']
    new_domain_name = replace_parent_domain(tag_name, args['product_tld'], args['hosted_zone'], end_with_period=False)
    print new_domain_name
