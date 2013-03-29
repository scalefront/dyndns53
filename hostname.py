



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Prints a hostname based on the current AWS instance's \"Name\" tag value.")
    parser.add_argument('-t','--truncate-name', help='Remove matching text from rhs of instance Name tag value.', required=True, dest='truncate_name')
    parser.add_argument('-z','--zone-domain-name', help='Zone Domain Name (e.g. ec2-pub.website.com)', required=True, dest='zone_domain_name')
    args = vars(parser.parse_args())

    from utils import get_current_instance_id, get_instance, replace_parent_domain
    instance_id = get_current_instance_id()
    instance = get_instance(instance_id)
    tag_name = instance.tags['Name']
    new_domain_name = replace_parent_domain(tag_name, args['truncate_name'], args['zone_domain_name'], end_with_period=False)
    print new_domain_name
