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


def main():
    version = get_distribution('squabble').version
    args = docopt.docopt(__doc__, version=version)

    print(args)

    if args['--verbose']:
        logger.setLevel('DEBUG')

    migrations = args['FILES']
    config_file = args['--config'] or config.discover_config_location()

    if config_file is None or not os.path.exists(config_file):
        print('Could not find a valid config file!')
        sys.exit(1)

    cfg = config.parse_config(config_file)

    for file_name in migrations:
        rules = config.parse_file_rules(file_name)
        engine = lint.Engine.from_config(cfg, rules)

        engine.lint(file_name)


if __name__ == '__main__':
    main()
