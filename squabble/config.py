import json
import os.path
import re
import subprocess

from . import logger


def discover_config_location():
    logger.debug('No config file given, trying to discover')

    possible_dirs = [
        '.',
        get_vcs_root(),
        os.path.expanduser('~')
    ]

    for d in possible_dirs:
        if d is None:
            continue

        logger.debug('Checking %s for a config file', d)

        file_name = os.path.join(d, '.squabblerc')
        if os.path.exists(file_name):
            return file_name

    return None


def get_vcs_root():
    return subprocess.getoutput(
        'git rev-parse --show-toplevel 2>/dev/null ||'
        'echo ""')


# TODO: extract config into a class rather than bare dict
def parse_config(config_file):
    with open(config_file, 'r') as fp:
        return json.load(fp)


def parse_file_rules(file_name):
    with open(file_name, 'r') as fp:
        text = fp.read()

    return extract_file_rules(text)


def extract_file_rules(text):
    '''
    Try to extract any file-level rule additions/suppressions.

    Valid lines are SQL line comments that enable or disable specific rules.

     >>> extract_file_rules('...\n-- enable:rule1 opt=foo arr=a,b,c')

     {'disable': [], 'enable': {'rule1': {'opt': 'foo', 'arr': ['a','b','c']}}}
    '''
    rules = {
        'enable': {},
        'disable': [],
    }

    comment_re = re.compile(r'--\s*(enable|disable):(\w+)(.*)', re.I)

    for line in text.splitlines():
        line = line.strip()

        m = re.match(comment_re, line)
        if m is None:
            continue

        action, rule, args = m.groups()

        if action == 'disable':
            rules['disable'].append(rule)

        elif action == 'enable':
            options = {}

            for opt in args.strip().split(' '):
                k, v = opt.split('=', 1)

                if ',' in v:
                    v = v.split(',')

                options[k] = v

            rules['enable'][rule] = options

    return rules
