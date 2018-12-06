import json
import os.path
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


def check_config_rules(config, file_name):
    with open(file_name, 'r') as fp:
        text = fp.read()

    file_config = extract_file_rules(text)

    print('checking', file_config, text)


def extract_file_rules(text):
    rules = {
        'enable': [],
        'disable': []
    }

    for line in text.splitlines():
        line = line.strip()

        if not line.startswith('-- '):
            continue

        for word in line.split(' '):
            split = word.split(':')

            if len(split) != 2:
                continue

            elif split[0] in ('enable', 'disable'):
                rules[split[0]].append(split[1])

    return rules
