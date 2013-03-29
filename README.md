# DynDns53

Create a Route53 A-record or CNAME from AWS instance's public or private identity.

## Example usage:

Create a Route53 A-record mapping the ec2 instance's tag name value to its public ip address.

dyndns53.py --truncate-name="a.b.com" --zone-domain-name="ec2-pub.a.b.com" --identity="public" --record-type="A"
