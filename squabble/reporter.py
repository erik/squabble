# coding: utf-8

import functools
import sys

from colorama import Fore, Back, Style
import pglast


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


def location_for_issue(issue):
    """
    Correctly return the offset into the file for this issue, or None if it
    cannot be determined.
    """

    if issue.node and issue.node.location != pglast.Missing:
        return issue.node.location.value

    return issue.location


def issue_to_file_location(issue, contents):
    """
    Given a `LintIssue` (which may or may not have a `pglast.Node` with a
    `location` field) and the contents of the file containing that node, return
    the (line_str, line, column) that node is located at, or `('', 1, 0)`.
    """

    loc = location_for_issue(issue)

    if loc is None:
        return ('', 1, 0)

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


def _format_message(issue):
    if issue.message_text:
        return issue.message_text

    template = issue.rule.MESSAGES[issue.message_id]
    params = issue.message_params or {}

    return template.format(**params)


def _issue_info(issue, file_contents):
    line, line_num, column = issue_to_file_location(issue, file_contents)

    formatted = _format_message(issue)

    return {
        'line_text': line,
        'line': line_num,
        'column': column,
        'message_formatted': formatted,
        **issue._asdict()
    }


_SIMPLE_FORMAT = '{file}:{line}:{column} {severity}: {message_formatted}'


@reporter("plain")
def plain_text_reporter(issue, file_contents):
    info = _issue_info(issue, file_contents)

    _print_err(_SIMPLE_FORMAT.format(**info))

    if info['line_text'] != '':
        _print_err(info['line_text'])
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

    fmt = '{bold}{file}:{reset}{line}:{column}{reset} '\
        '{red}{severity}{reset}: {message_formatted}'

    _print_err(fmt.format(**{
        **color,
        **info
    }))

    if info['line_text'] != '':
        arrow = ' ' * info['column'] + '^'
        _print_err(info['line_text'])
        _print_err(Style.BRIGHT + arrow + Style.RESET_ALL)
