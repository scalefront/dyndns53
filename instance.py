import argparse

def get_instance(instance_id):
    from boto.ec2.connection import EC2Connection
    cxn = EC2Connection()
    reservations = cxn.get_all_instances([instance_id])
    return reservations[0].instances[0]

def get_instance_name(instance):
    return instance.tags['Name']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prints the value of tag "Name" for the specified instance id.')
    parser.add_argument('-i','--instance-id', help='Instance ID', required=True, dest='instance_id')
    args = vars(parser.parse_args())
    instance = get_instance(args['instance_id'])
    name = get_instance_name(instance)
    print name
