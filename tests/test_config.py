from squabble import config


def test_extract_file_rules():
    text = '''
foo
-- enable:foo k1=v1 k2=v2
bar
-- disable:abc enable:xyz
'''

    rules = config.extract_file_rules(text)

    expected = {
        'enable': {'foo': {'k1': 'v1', 'k2': 'v2'}},
        'disable': ['abc'],
    }

    assert expected == rules
