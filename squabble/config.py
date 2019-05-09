import collections
import copy
import json
import logging
import os.path
import re
import subprocess

from squabble import SquabbleException


logger = logging.getLogger(__name__)


Config = collections.namedtuple('Config', [
    'reporter',
    'plugins',
    'rules'
])


# TODO: Move these out somewhere else, feels gross to have them hardcoded.
DEFAULT_CONFIG = dict(
    reporter='plain',
    plugins=[],
    rules={}
)

PRESETS = {
    'postgres': {
        'description': (
            'A sane set of defaults that checks for obviously '
            'dangerous Postgres migrations and query antipatterns.'
        ),
        'config': {
            'rules': {
                'DisallowRenameEnumValue': {},
                'DisallowChangeColumnType': {},
                'DisallowNotIn': {},
                'DisallowTimetzType': {},
                'DisallowPaddedCharType': {},
                'DisallowTimestampPrecision': {},
            }
        }
    },

    'postgres-zero-downtime': {
        'description': (
            'A set of rules focused on preventing downtime during schema '
            'migrations on busy Postgres databases.'
        ),
        'config': {
            'rules': {
                'AddColumnDisallowConstraints': {
                    'disallowed': ['DEFAULT', 'NOT NULL', 'UNIQUE']
                },
                'DisallowRenameEnumValue': {},
                'DisallowChangeColumnType': {},
                'RequireConcurrentIndex': {},
            }
        }
    },

    'full': {
        'description': ('Every rule that ships with squabble. The output will '
                        'be noisy (and nonsensical), but it\'s probably a good '
                        'starting point to figure out which rules are useful.'),
        'config': {
            'rules': {
                'AddColumnDisallowConstraints': {
                    'disallowed': ['DEFAULT', 'NOT NULL', 'UNIQUE', 'FOREIGN']
                },
                'RequireConcurrentIndex': {},
                'DisallowRenameEnumValue': {},
                'DisallowChangeColumnType': {},
                'DisallowFloatTypes': {},
                'DisallowNotIn': {},
                'DisallowTimetzType': {},
                'DisallowPaddedCharType': {},
                'DisallowTimestampPrecision': {},
                'RequirePrimaryKey': {},
                # Yes, these are incompatible.
                'DisallowForeignKey': {},
                'RequireForeignKey': {},
            }
        }
    }
}


class UnknownPresetException(SquabbleException):
    """Raised when user tries to apply a preset that isn't defined."""
    def __init__(self, preset):
        super().__init__('unknown preset: "%s"' % preset)


def discover_config_location():
    """
    Try to locate a config file in some likely locations.

    Used when no config path is specified explicitly. In order, this
    will check for a file named ``.squabblerc``:

    - in the current directory.
    - in the root of the repository (if working in a git repo).
    - in the user's home directory.
    """
    possible_dirs = [
        '.',
        _get_vcs_root(),
        os.path.expanduser('~')
    ]

    for d in possible_dirs:
        if d is None:
            continue

        logger.debug('checking %s for a config file', d)

        file_name = os.path.join(d, '.squabblerc')
        if os.path.exists(file_name):
            logger.debug('using "%s" for configuration', file_name)
            return file_name

    logger.debug('no config file found')
    return None


def _get_vcs_root():
    """
    Return the path to the root of the Git repository for the current
    directory, or empty string if not in a repository.
    """
    return subprocess.getoutput(
        'git rev-parse --show-toplevel 2>/dev/null || echo ""')


def get_base_config(preset_names=None):
    """
    Return a basic config value that can be overridden by user configuration
    files.

    :param preset_names: The named presets to use (applied in order), or None
    """
    if not preset_names:
        return Config(**DEFAULT_CONFIG)

    preset_settings = {}
    for name in preset_names:
        if name not in PRESETS:
            raise UnknownPresetException(name)

        preset_settings = _merge_dicts(preset_settings, PRESETS[name])

    return Config(**{
        **DEFAULT_CONFIG,
        **preset_settings['config']
    })


def _parse_config_file(config_file):
    if not config_file:
        return {}

    with open(config_file, 'r') as fp:
        return json.load(fp)


def load_config(config_file, preset_names=None, reporter_name=None):
    """
    Load configuration from a file, optionally applying a predefined
    set of rules.

    :param config_file: Path to JSON file containing user configuration.
    :type config_file: str
    :param preset_name: Preset to use as a base before applying user
                        configuration.
    :type preset_name: str
    :param reporter_name: Override the reporter named in configuration.
    :type reporter_name: str
    """
    base = get_base_config(preset_names)
    config = _parse_config_file(config_file)

    rules = copy.deepcopy(base.rules)
    for name, rule in config.get('rules', {}).items():
        rules[name] = rule

    return Config(
        reporter=reporter_name or config.get('reporter', base.reporter),
        plugins=config.get('plugins', base.plugins),
        rules=rules
    )


def apply_file_config(base, contents):
    """
    Given a base configuration object and the contents of a file,
    return a new config that applies any file-specific rule
    additions/deletions.
    """
    # Operate on a copy so we don't mutate the base config
    file_rules = copy.deepcopy(base.rules)

    rules = _extract_file_rules(contents)

    for rule, opts in rules['enable'].items():
        file_rules[rule] = opts

    for rule in rules['disable']:
        del file_rules[rule]

    return base._replace(rules=file_rules)


def _extract_file_rules(text):
    """
    Try to extract any file-level rule additions/suppressions.

    Valid lines are SQL line comments that enable or disable specific rules.

    >>> rules = _extract_file_rules('-- enable:rule1 arr=a,b,c')
    >>> rules['disable']
    []
    >>> rules['enable']
    {'rule1': {'arr': ['a', 'b', 'c']}}
    """
    rules = {
        'enable': {},
        'disable': [],
    }

    comment_re = re.compile(r'--\s*(enable|disable):(\w+)(.*?)$', re.I)

    for line in text.splitlines():
        line = line.strip()

        m = re.match(comment_re, line)
        if m is None:
            continue

        action, rule, opts = m.groups()

        if action == 'disable':
            rules['disable'].append(rule)

        elif action == 'enable':
            rules['enable'][rule] = _parse_options(opts)

    return rules


def _parse_options(opts):
    """
    Given a string of space-separated `key=value` pairs, return a dictionary of
    `{"key": "value"}`. Note the value will always be returned as a string, and
    no further parsing will be attempted.

    >>> opts = _parse_options('k=v abc=1,2,3')
    >>> opts == {'k': 'v', 'abc': ['1', '2', '3']}
    True
    >>> _parse_options('k="1,2","3,4"')
    {'k': ['1,2', '3,4']}
    """
    options = {}

    # Either a simple quoted string or a bare value
    value = r'(?:(?:"([^"]+)")|([^,\s]+))'

    # Value followed by zero or more values
    value_list = r'{0}(?:,{0})*'.format(value)

    value_regex = re.compile(value)
    kv_regex = re.compile(r'(\w+)=({0})'.format(value_list))

    # 'k=1,2' => ('k', '1,2')
    for match in re.finditer(kv_regex, opts):
        key, val = match.group(1, 2)

        # value_regex will return ('string', '') or ('', 'value')
        values = [a or b for a, b in re.findall(value_regex, val)]

        # Collapse single len lists into scalars
        options[key] = values[0] if len(values) == 1 else values

    return options


def _merge_dicts(a, b):
    """
    Combine the values of two (possibly nested) dictionaries.

    Values in ``b`` will take precedence over those in ``a``. This function
    will return a new dictionary rather than mutating its arguments.

    >>> a = {'foo': {'a': 1, 'b': 2}}
    >>> b = {'foo': {'b': 3, 'c': 4}, 'bar': 5}
    >>> m = _merge_dicts(a, b)
    >>> m == {'foo': {'a': 1, 'b': 3, 'c': 4}, 'bar': 5}
    True
    """
    def _inner(x, y, out):
        """Recursive helper function which mutates its arguments."""
        for k in x.keys() | y.keys():
            xv, yv = x.get(k, {}), y.get(k, {})

            if isinstance(xv, dict) and isinstance(yv, dict):
                out[k] = _inner(xv, yv, {})
            else:
                out[k] = yv if k in y else xv
        return out

    return _inner(a, b, {})
