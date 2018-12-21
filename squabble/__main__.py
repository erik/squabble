'''
Usage:
  squabble [options] [FILES...]
  squabble (-h | --help)

Arguments:
  FILES              One or more files to lint

Options:
  -c --config=PATH     Path to configuration file
  -h --help            Show this screen
  -p --preset=PRESET   Start with a base preset rule configuration
  -P --list-presets    List the available preset configurations
  -r --show-rule=RULE  Show detailed information about RULE
  -R --list-rules      Print out information about all available rules
  -V --verbose         Turn on debug level logging
  -v --version         Show version information
'''

import json
import os.path
import sys
from pkg_resources import get_distribution

import colorama
import docopt
from colorama import Fore, Back, Style

import squabble
from squabble import config, lint, logger, rules, reporter


def main():
    version = get_distribution('squabble').version
    args = docopt.docopt(__doc__, version=version)

    if args['--verbose']:
        logger.setLevel('DEBUG')

    migrations = args['FILES']
    config_file = args['--config'] or config.discover_config_location()
    preset = args['--preset']

    if args['--list-presets']:
        return list_presets()

    if not config_file or not os.path.exists(config_file):
        print('Could not find a valid config file!')
        sys.exit(1)

    base_config = config.parse_config_file(config_file, preset)

    # Load all of the rule classes into memory
    rules.load(plugin_paths=base_config.plugins)

    if args['--list-rules']:
        return list_rules()
    elif args['--show-rule']:
        return show_rule(name=args['--show-rule'])

    issues = []
    for file_name in migrations:
        issues += lint_file(base_config, file_name)

    reporter.report(base_config.reporter, issues)

    # Make sure we have an error status if something went wrong.
    if issues:
        sys.exit(1)


def lint_file(base_config, file_name):
    file_config = config.apply_file_config(base_config, file_name)
    return lint.check_file(file_config, file_name)


def show_rule(name):
    color = {
        'bold': Style.BRIGHT,
        'reset': Style.RESET_ALL,
    }

    try:
        rule = rules.Registry.get_meta(name)
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

    all_rules = sorted(rules.Registry.all(), key=lambda r: r['meta']['name'])

    for rule in all_rules:
        meta = rule['meta']

        print('{bold}{name: <32}{reset} {description}'.format(**{
            **color,
            **meta
        }))


def list_presets():
    for name, preset in config.PRESETS.items():
        print('{bold}{name}{reset} - {description}'.format(
            name=name,
            description=preset.get('description', ''),
            bold=Style.BRIGHT,
            reset=Style.RESET_ALL
        ))

        # npm here i come
        left_pad = '    '
        cfg = json.dumps(preset['config'], indent=4)\
                  .replace('\n', '\n' + left_pad)
        print(left_pad + cfg)


if __name__ == '__main__':
    colorama.init()
    main()
