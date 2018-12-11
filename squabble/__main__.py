''' TODO: description

Usage:
  squabble [options] FILES...
  squabble (-h | --help)

Arguments:
  FILES    TODO description

Options:
  -c --config=PATH   Path to configuration file
  -h --help          Show this screen
  -V --verbose       Turn on debug level logging
  -v --version       Show version information
'''

import os.path
import sys
from pkg_resources import get_distribution

import colorama
import docopt

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

    base_config = config.parse_config(config_file)

    # Load all of the rule classes into memory
    rules.load(plugins=base_config.plugins)

    issues = []
    for file_name in migrations:
        issues = lint_file(base_config, file_name)

    reporter.report(base_config, issues)


def lint_file(base_config, file_name):
    file_config = config.apply_file_config(base_config, file_name)
    return lint.check_file(file_config, file_name)


if __name__ == '__main__':
    colorama.init()
    main()
