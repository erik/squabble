import collections
import json
import os.path
import re
import subprocess

from . import logger


Config = collections.namedtuple('Config', [
    'reporter',
    'plugins',
    'rules'
])


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


def parse_config(config_file):
    with open(config_file, 'r') as fp:
        obj = json.load(fp)

    return Config(
        reporter=obj.get('reporter', 'plain'),
        plugins=obj.get('plugins', []),
        rules=obj.get('rules',  {}),
    )


def apply_file_config(base, file_name):
    """
    Given a base configuration object and a file, return a new config that
    applies any file-specific rule additions/deletions
    """

    # Operate on a copy so we don't mutate the base config
    config = base._asdict()

    rules = parse_file_rules(file_name)

    for rule, opts in rules['enable'].items():
        config['rules'][rule] = opts

    for rule in rules['disable']:
        del config['rules'][rule]

    return Config(**config)


def parse_file_rules(file_name):
    with open(file_name, 'r') as fp:
        text = fp.read()

    return extract_file_rules(text)


def extract_file_rules(text):
    """
    Try to extract any file-level rule additions/suppressions.

    Valid lines are SQL line comments that enable or disable specific rules.

     >>> extract_file_rules('...\n-- enable:rule1 opt=foo arr=a,b,c')

     {'disable': [], 'enable': {'rule1': {'opt': 'foo', 'arr': ['a','b','c']}}}
    """

    rules = {
        'enable': {},
        'disable': [],
    }

    comment_re = re.compile(r'--\s*(enable|disable):(\w+)(.*?)$', re.I)

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
                if opt == '':
                    continue

                k, v = opt.split('=', 1)

                if ',' in v:
                    v = v.split(',')

                options[k] = v

            rules['enable'][rule] = options

    return rules
