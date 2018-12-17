'''
Usage:
  squabble [options] [FILES...]
  squabble (-h | --help)

Arguments:
  FILES              One or more files to lint

Options:
  -c --config=PATH     Path to configuration file
  -h --help            Show this screen
  -r --show-rule=RULE  Show detailed information about RULE
  -R --list-rules      Print out information about all available rules
  -V --verbose         Turn on debug level logging
  -v --version         Show version information
'''

import os.path
import sys
from pkg_resources import get_distribution

import colorama
import docopt
from colorama import Fore, Back, Style

import squabble
from squabble import config
from squabble import lint
from squabble import logger
from squabble import rules
from squabble import reporter


def main():
    version = get_distribution('squabble').version
    args = docopt.docopt(__doc__, version=version)

    if args['--verbose']:
        logger.setLevel('DEBUG')

    migrations = args['FILES']
    config_file = args['--config'] or config.discover_config_location()

    if config_file is None or not os.path.exists(config_file):
        print('Could not find a valid config file!')
        sys.exit(1)

    base_config = config.parse_config_file(config_file)

    # Load all of the rule classes into memory
    rules.load(plugins=base_config.plugins)

    if args['--list-rules']:
        return list_rules()
    elif args['--show-rule']:
        return show_rule(args['--show-rule'])

    issues = []
    for file_name in migrations:
        issues += lint_file(base_config, file_name)

    reporter.report(base_config, issues)


def lint_file(base_config, file_name):
    file_config = config.apply_file_config(base_config, file_name)
    return lint.check_file(file_config, file_name)


def show_rule(name):
    color = {
        'bold': Style.BRIGHT,
        'reset': Style.RESET_ALL,
    }

    try:
        rule = rules.Rule.get(name)
    except squabble.UnknownRuleException:
        print('{bold}Unknown rule:{reset} {name}'.format(**{
            'name': name,
            **color
        }))
        sys.exit(1)

    meta = rule['meta']
    print('{bold}{name}{reset} - {description}\n{help}'.format(**{
        **meta,
        **color
    }))


def list_rules():
    color = {
        'bold': Style.BRIGHT,
        'reset': Style.RESET_ALL,
    }

    all_rules = sorted(rules.Rule.all(), key=lambda r: r['meta']['name'])

    for rule in all_rules:
        meta = rule['meta']

        print('{bold}{name: <32}{reset} {description}'.format(**{
            **color,
            **meta
        }))


if __name__ == '__main__':
    colorama.init()
    main()
