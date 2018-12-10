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

import docopt

from . import config
from . import lint
from . import logger
from . import rules


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

    for file_name in migrations:
        lint_file(base_config, file_name)


def lint_file(base_config, file_name):
    file_config = config.apply_file_config(base_config, file_name)
    errors = lint.check_file(file_config, file_name)

    for e in errors:
        print('lint error:', e)


if __name__ == '__main__':
    main()
