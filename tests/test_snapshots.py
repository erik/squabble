"""Integration style tests against the files in `./sql`"""

import glob
import json

import pytest

import squabble.cli
from squabble import config, lint, reporter, rule

SQL_FILES = glob.glob('tests/sql/*.sql')
OUTPUT_MARKER = '-- >>> '


def setup_module(_mod):
    rule.load_rules(plugin_paths=[])


def expected_output(file_name):
    with open(file_name, 'r') as fp:
        lines = fp.readlines()

    expected = []
    for line in lines:
        if not line.startswith(OUTPUT_MARKER):
            continue

        _, out = line.split(OUTPUT_MARKER, 1)
        expected.append(json.loads(out))

    return expected


@pytest.mark.parametrize('file_name', SQL_FILES)
def test_snapshot(file_name):
    with open(file_name, 'r') as fp:
        contents = fp.read()

    expected = expected_output(file_name)

    if not expected:
        pytest.skip('no output configured')

    base_cfg = config.get_base_config()
    cfg = config.apply_file_config(base_cfg, contents)

    issues = lint.check_file(cfg, file_name, contents)

    assert len(issues) == len(expected)

    for i, e in zip(issues, expected):
        info = reporter._issue_info(i, contents)
        actual = {
            k: info.get(k)
            for k in e.keys()
        }

        assert actual == e


@pytest.mark.parametrize('reporter_name', reporter._REPORTERS.keys())
def test_reporter_sanity(reporter_name):
    """
    Make sure all the reporters can at least format all of the
    issues generated without errors.
    """
    base_cfg = config.get_base_config()

    issues = []
    files = {}

    for file_name in SQL_FILES:
        with open(file_name, 'r') as fp:
            contents = fp.read()
            files[file_name] = contents

        cfg = config.apply_file_config(base_cfg, contents)
        issues.extend(lint.check_file(cfg, file_name, contents))

    reporter.report(reporter_name, issues, files)


def test_cli_linter():
    """Dumb test to make sure things are wired correctly in CLI."""
    base_cfg = config.get_base_config()
    exit_status = squabble.cli.run_linter(base_cfg, SQL_FILES, expanded=True)

    # Exit status 1 means that lint issues occurred, not that the process
    # itself failed.
    assert exit_status == 1
