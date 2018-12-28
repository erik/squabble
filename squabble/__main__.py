import sys

import colorama

from squabble import cli


def main():
    colorama.init()
    status = cli.main()

    if status:
        sys.exit(status)


if __name__ == '__main__':
    main()
