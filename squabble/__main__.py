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

    print(args)

    if args['--verbose']:
        logger.setLevel('DEBUG')

    migrations = args['FILES']
    config_file = args['--config'] or config.discover_config_location()

    if config_file is None or not os.path.exists(config_file):
        print('Could not find a valid config file!')
        sys.exit(1)

    cfg = config.parse_config(config_file)
    rule_set = rules.load()

    for file_name in migrations:
        file_rules = config.parse_file_rules(file_name)
        enabled_rules = filter(
            lambda r: (
                (r.name in cfg['rules'] or r.name in file_rules['enabled']) and
                (r.name not in file_rules['disabled'])),
            rule_set)

        engine = lint.Engine.from_config(cfg, enabled_rules)
        engine.lint(file_name)


if __name__ == '__main__':
    main()
