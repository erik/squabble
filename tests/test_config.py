import copy
from unittest.mock import patch

import pytest

from squabble import config


def test_extract_file_rules():
    text = '''
foo
-- enable:foo k1=v1 k2=v2
bar
-- disable:abc enable:xyz
'''

    rules = config._extract_file_rules(text)

    expected = {
        'enable': {'foo': {'k1': 'v1', 'k2': 'v2'}},
        'disable': ['abc'],
        'skip_file': False
    }

    assert expected == rules


def test_extract_file_rules_with_prefix():
    text = '''
foo
-- squabble-enable:foo k1=v1 k2=v2
bar
-- squabble-disable:abc enable:xyz
-- squabble-disable
'''

    rules = config._extract_file_rules(text)

    expected = {
        'enable': {'foo': {'k1': 'v1', 'k2': 'v2'}},
        'disable': ['abc'],
        'skip_file': True
    }

    assert expected == rules


def test_get_base_config_without_preset():
    cfg = config.get_base_config()
    assert cfg == config.Config(**config.DEFAULT_CONFIG)


def test_get_base_config_with_preset():
    cfg = config.get_base_config(['postgres'])
    assert cfg.rules == config.PRESETS['postgres']['config']['rules']


def test_unknown_preset():
    with pytest.raises(config.UnknownPresetException):
        config.get_base_config(preset_names=['asdf'])


def test_merging_presets():
    cfg = config.get_base_config(preset_names=['postgres', 'full'])
    merged = config._merge_dicts(
        config.PRESETS['postgres']['config']['rules'],
        config.PRESETS['full']['config']['rules']
    )
    assert cfg.rules == merged


@patch('squabble.config._extract_file_rules')
def test_apply_file_config(mock_extract):
    mock_extract.return_value = {
        'enable': {'baz': {'a': 1}},
        'disable': ['bar'],
        'skip_file': False
    }

    orig = config.Config(reporter='', plugins=[], rules={'foo': {}, 'bar': {}})
    base = copy.deepcopy(orig)

    modified = config.apply_file_config(base, 'file_name')

    assert modified.rules == {'foo': {}, 'baz': {'a': 1}}

    # Make sure nothing has been mutated
    assert base == orig


@patch('squabble.config._extract_file_rules')
def test_apply_file_config_with_skip_file(mock_extract):
    mock_extract.return_value = {
        'enable': {},
        'disable': [],
        'skip_file': True
    }

    orig = config.Config(reporter='', plugins=[], rules={})
    base = copy.deepcopy(orig)

    modified = config.apply_file_config(base, 'file_name')

    assert modified is None


@patch('squabble.config._get_vcs_root')
@patch('os.path.expanduser')
@patch('os.path.exists')
def test_discover_config_location(mock_exists, mock_expand, mock_vcs):
    mock_exists.return_value = False
    mock_expand.return_value = 'user'
    mock_vcs.return_value = 'gitrepo'

    config.discover_config_location()

    mock_exists.assert_any_call('./.squabblerc')
    mock_exists.assert_any_call('gitrepo/.squabblerc')
    mock_exists.assert_any_call('user/.squabblerc')
