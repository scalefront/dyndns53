
_current_instance_id = None
def get_current_instance_id():
    global _current_instance_id
    if _current_instance_id is None:
       import subprocess
       p = subprocess.Popen("wget -q -O - http://169.254.169.254/latest/meta-data/instance-id", stdout=subprocess.PIPE, shell=True)
       (instance_id, err) = p.communicate()
       _current_instance_id = instance_id
    return _current_instance_id

_instances = {}
def get_instance(instance_id):
    global _instances
    if instance_id in _instances:
        instance = _instances[instance_id]
    else:
        from boto.ec2.connection import EC2Connection
        cxn = EC2Connection()
        reservations = cxn.get_all_instances([instance_id])
        instance = reservations[0].instances[0]
        # Add instance to cache
        _instances[instance_id] = instance
    return instance

def get_current_instance():
    current_instance_id = get_current_instance_id()
    instance = get_instance(current_instance_id)
    return instance

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

def join_domain(subdomain, domain):
    """
    >>> join_domain('a.b.c', 'd.e')
    'a.b.c.d.e'
    >>> join_domain('a', 'b')
    'a.b'
    >>> join_domain('*', 'a.b.c')
    '*.a.b.c'
    """
    subdomain = subdomain.rstrip('.')
    domain = domain.lstrip('.')
    fqdn = '.'.join([subdomain, domain])
    return fqdn

def replace_parent_domain(domain_name, old_parent_domain, new_parent_domain, end_with_period=True):
    """
    >>> replace_parent_domain('web1.qa.apple.com', 'apple.com', 'aws-public.apple.com')
    'web1.qa.aws-public.apple.com.'
    >>> replace_parent_domain('a.b.c.d.e', 'c.d.e', 'y.z', False)
    'a.b.y.z'
    """
    truncated_domain = _truncate_domain(domain_name, old_parent_domain)
    new_domain_name = join_domain(truncated_domain, new_parent_domain)
    if end_with_period:
        new_domain_name += '.'
    return new_domain_name
