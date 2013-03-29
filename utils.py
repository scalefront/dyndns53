def get_current_instance_id():
    import subprocess
    p = subprocess.Popen("wget -q -O - http://169.254.169.254/latest/meta-data/instance-id", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    return output

def get_instance(instance_id):
    from boto.ec2.connection import EC2Connection
    cxn = EC2Connection()
    reservations = cxn.get_all_instances([instance_id])
    return reservations[0].instances[0]

def _truncate_domain(domain_name, domain_suffix):
    """
    >>> _truncate_domain('web1.qa.apple.com', 'apple.com')
    'web1.qa'
    >>> _truncate_domain('a.b.c.d.e', '.c.d.e')
    'a.b'
    """
    ndx = domain_name.rfind(domain_suffix)
    truncated_domain = domain_name[:ndx]
    truncated_domain = truncated_domain.rstrip('.')
    return truncated_domain

def replace_parent_domain(domain_name, old_parent_domain, new_parent_domain, end_with_period=True):
    """
    >>> generate_fqdn('web1.qa.apple.com', 'apple.com', 'aws-public.apple.com')
    'web1.qa.aws-public.apple.com'
    >>> generate_fqdn('a.b.c.d.e', 'c.d.e', 'y.z')
    'a.b.y.z'
    """
    truncated_domain = _truncate_domain(domain_name, old_parent_domain)
    new_domain_name = '%s.%s.' % (truncated_domain, new_parent_domain)
    if not end_with_period:
        new_domain_name = new_domain_name.rstrip('.')
    return new_domain_name
