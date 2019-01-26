""" file:   aws.py
    author: Jess Robertson, @jesserobertson
    date:   Saturday, 26 January 2019

    description: Utilities to help with AWS stuff
"""

import logging
import os
import re

LOGGER = logging.getLogger('geoserverless')
LOGGER.setLevel('INFO')

def get_credentials(profile=None):
    """ Get AWS credentials from the credentials file

        Parameters:
            profile - the AWS profile to use. Optional, if
                None defaults to 'default'.

        Returns:
            a dict containing the AWS credentials
    """
    # Get credentials
    LOGGER.info("Parsing ~/.aws/credentials for profiles")
    profile_pattern = re.compile(r'(?<=\[)[^\[\]]+')
    credsfile = os.path.expanduser('~/.aws/credentials')
    with open(credsfile, 'r') as stream:
        all_creds, current_name = {}, None
        for line in stream:
            ismatch = profile_pattern.search(line)
            if ismatch:
                current_name = ismatch.group(0)
                all_creds[current_name] = {}
            elif current_name is None:
                raise ValueError('Malformed ~/.aws/config file')
            elif line.strip() == '':
                continue
            else:
                key, value = tuple(line.split('='))
                all_creds[current_name][key.strip()] = value.strip()

    # Get the credentials we care about
    profile = profile or 'default'
    try:
        return {
            'access_key': all_creds[profile]['aws_access_key_id'],
            'secret_key': all_creds[profile]['aws_secret_access_key']
        }
    except KeyError:
        msg = 'Unknown profile {0}, available profiles are {1}'.format(profile, all_creds.keys())
        LOGGER.error(msg)
        raise ValueError(msg)
