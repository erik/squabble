import logging
import sys

import colorama

from squabble import cli


def main():
    logging.basicConfig()
    colorama.init()
    status = cli.main()

    if status:
        sys.exit(status)


if __name__ == '__main__':
    main()
