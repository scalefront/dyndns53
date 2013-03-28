#!/usr/bin/env python
import argparse

def get_current_instance_id():
    import subprocess
    p = subprocess.Popen("wget -q -O - http://169.254.169.254/latest/meta-data/instance-id", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prints the instance id for the current instance (must be run from an EC2 instance).')
    name = get_current_instance_id()
    print name
