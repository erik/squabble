import functools
import sys

from colorama import Fore, Back, Style


_REPORTERS = {}


def reporter(name):
    def wrapper(fn):
        _REPORTERS[name] = fn

        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapped

    return wrapper


def report(config, issues):
    fn = _REPORTERS[config.reporter]
    files = {}

    for i in issues:
        # Cache the file contents
        if i.file is not None and i.file not in files:
            with open(i.file, 'r') as fp:
                files[i.file] = fp.read()

        file_contents = files.get(i.file, '')
        fn(i, file_contents)


def issue_to_file_location(issue, contents):
    """
    Given a `LintIssue` (which may or may not have a `pglast.Node` with a
    `location` field) and the contents of the file containing that node, return
    the (line_str, line, column) that node is located at, or `('', 1, 0)`.
    """

    if issue.node is None or not hasattr(issue.node, 'location'):
        return ('', 1, 0)

    loc = issue.node.location.value
    lines = contents.splitlines()

    for i, line in enumerate(lines, start=1):
        if loc <= len(line):
            return (line, i, loc)

        # Add 1 to count the newline char.
        # TODO: won't work with \r\n
        loc -= len(line) + 1

    return ('', 1, 0)


def _print_err(msg):
    print(msg, file=sys.stderr)


def _issue_info(issue, file_contents):
    line, line_num, column = issue_to_file_location(issue, file_contents)

    return {
        'file': issue.file,
        'line': line,
        'line_num': line_num,
        'column': column,
        'severity': issue.severity,
        'msg': issue.msg
    }


_SIMPLE_FORMAT = '{file}:{line_num}:{column} {severity}: {msg}'


@reporter("plain")
def plain_text_reporter(issue, file_contents):
    info = _issue_info(issue, file_contents)

    _print_err(_SIMPLE_FORMAT.format(**info))

    if info['line'] != '':
        _print_err(info['line'])
        _print_err(' ' * info['column'] + '^')
        _print_err('')


@reporter('color')
def color_reporter(issue, file_contents):
    info = _issue_info(issue, file_contents)

    color = {
        'bold': Style.BRIGHT,
        'red': Fore.RED,
        'white': Fore.WHITE,
        'reset': Style.RESET_ALL,
    }

    fmt = '{bold}{file}:{reset}{line_num}:{column}{reset} '\
        '{red}{severity}{reset}: {msg}'

    _print_err(fmt.format(**{
        **color,
        **info
    }))

    if info['line'] != '':
        arrow = ' ' * info['column'] + '👆'
        _print_err(info['line'])
        _print_err(arrow)
        _print_err('')
