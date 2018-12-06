from squabble import config


def test_extract_file_rules():
    text = '''
foo
-- disable:enable:disable
-- disable:123 enable:456
bar
-- disable:abc enable:xyz
'''

    rules = config.extract_file_rules(text)

    assert rules == {
        'enable': ['456', 'xyz'],
        'disable': ['123', 'abc'],
    }
