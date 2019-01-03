"""
Usage:
  squabble [options] [PATHS...]
  squabble (-h | --help)

Arguments:
  PATHS                Files or directories to lint. If given a directory, will
                       recursively traverse the path and lint all files ending
                       in `.sql`

Options:
  -c --config=PATH     Path to configuration file
  -e --explain=CODE    Show explanation of a rule's message code.
  -h --help            Show this screen
  -p --preset=PRESET   Start with a base preset rule configuration
  -P --list-presets    List the available preset configurations
  -r --show-rule=RULE  Show detailed information about RULE
  -R --list-rules      Print out information about all available rules
  -V --verbose         Turn on debug level logging
  -v --version         Show version information
"""

import glob
import json
import os.path
import sys

import docopt
from colorama import Style
from pkg_resources import get_distribution

import squabble
import squabble.message
from squabble import config, lint, logger, reporter, rule


def main():
    version = get_distribution('squabble').version
    args = docopt.docopt(__doc__, version=version)
    return dispatch_args(args)


def dispatch_args(args):
    """
    Handle the command line arguments as parsed by ``docopt``. Calls the
    subroutine implied by the combination of command line flags and returns the
    exit status (or ``None``, if successful) of the program.

    Note that some exceptional conditions will terminate the program directly.
    """
    if args['--verbose']:
        logger.setLevel('DEBUG')

    if args['--list-presets']:
        return list_presets()

    config_file = args['--config'] or config.discover_config_location()
    if config_file and not os.path.exists(config_file):
        sys.exit('%s: no such file or directory' % config_file)

    base_config = config.load_config(config_file, preset_name=args['--preset'])

    # Load all of the rule classes into memory (need to do this now to
    # be able to list all rules / show rule details)
    rule.load_rules(plugin_paths=base_config.plugins)

    if args['--list-rules']:
        return list_rules()

    if args['--show-rule']:
        return show_rule(name=args['--show-rule'])

    if args['--explain']:
        return explain_message(code=args['--explain'])

    return run_linter(base_config, args['PATHS'])


def run_linter(base_config, paths):
    """
    Run linter against all SQL files contained in ``paths``.

    ``paths`` may contain both files and directories.
    """
    files = collect_files(paths)

    issues = []
    for file_name in files:
        file_config = config.apply_file_config(base_config, file_name)
        issues += lint.check_file(file_config, file_name)

    reporter.report(base_config.reporter, issues)

    # Make sure we have an error status if something went wrong.
    return 1 if issues else 0


def collect_files(paths):
    """
    Given a list of files or directories, return all named files as well as
    any files ending in `.sql` in the directories.
    """
    files = []

    for path in map(os.path.expanduser, paths):
        if not os.path.exists(path):
            sys.exit('%s: no such file or directory' % path)

        elif os.path.isdir(path):
            sql = os.path.join(path, '**/*.sql')
            files.extend(glob.iglob(sql, recursive=True))

        else:
            files.append(path)

    return files


def show_rule(name):
    """Print information about rule named ``name``."""
    color = {
        'bold': Style.BRIGHT,
        'reset': Style.RESET_ALL,
    }

    try:
        meta = rule.Registry.get_meta(name)
    except squabble.UnknownRuleException:
        sys.exit('{bold}Unknown rule:{reset} {name}'.format(**{
            'name': name,
            **color
        }))

    print('{bold}{name}{reset} - {description}\n{help}'.format(**{
        **meta,
        **color
    }))


def list_rules():
    """Print out all registered rules and brief description of what they do."""
    color = {
        'bold': Style.BRIGHT,
        'reset': Style.RESET_ALL,
    }

    all_rules = sorted(rule.Registry.all(), key=lambda r: r['name'])

    for meta in all_rules:
        print('{bold}{name: <32}{reset} {description}'.format(**{
            **color,
            **meta
        }))


def explain_message(code):
    """Print out the more detailed explanation of the given message code."""
    try:
        code = int(code)
        cls = squabble.message.Registry.by_code(code)
    except (ValueError, KeyError):
        sys.exit('{bold}Unknown message code:{reset} {code}'.format(
            bold=Style.BRIGHT,
            reset=Style.RESET_ALL,
            code=code
        ))

    print('{bold}{name}{reset}'.format(
        bold=Style.BRIGHT,
        reset=Style.RESET_ALL,
        name=cls.__name__
    ))

    print('\t', cls.explain() or 'No additional info.', sep='')


def list_presets():
    """Print out all the preset configurations."""
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
