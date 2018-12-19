import glob
import importlib
import importlib.util as import_util
import os.path

from squabble import logger, UnknownRuleException


def _load_plugin(directory):
    """
    Given an arbitrary directory, try to load all Python files in order
    to register the custom rule definitions.

    Nothing is done with the Python files once they're loaded, it is
    assumed that simply importing the module will be enough to have the
    side effect of registering the modules correctly.
    """

    logger.debug('trying to load "%s" as a plugin directory', directory)

    if not os.path.isdir(directory):
        raise NotADirectoryError('cannot load "%s": not a directory' % directory)

    files = os.path.join(directory, '*.py')
    pkg_name = os.path.basename(os.path.dirname(directory))

    for file_name in glob.glob(files):
        logger.debug('loading file "%s" to pkg "%s"', file_name, pkg_name)
        spec = import_util.spec_from_file_location(pkg_name, file_name)

        # Parse and execute the file
        mod = import_util.module_from_spec(spec)
        spec.loader.exec_module(mod)


def load(plugins):
    modules = glob.glob(os.path.dirname(__file__) + '/*.py')

    for mod in modules:
        mod_name = os.path.basename(mod)[:-3]

        if not os.path.isfile(mod) or mod_name.startswith('__'):
            continue

        importlib.import_module(__name__ + '.' + mod_name)

    # Import plugins last so their naming takes precedence
    for plug in plugins:
        _load_plugin(plug)


class Rule:
    REGISTRY = {}

    def __init__(self, options):
        self._options = options

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Rule._register(cls)

    @staticmethod
    def _register(cls):
        meta = cls.meta()
        name = meta['name']

        logger.debug('registering rule "%s"', name)

        Rule.REGISTRY[name] = {'class': cls, 'meta': meta}

    @staticmethod
    def get(name):
        meta = Rule.REGISTRY.get(name)
        if meta is None:
            raise UnknownRuleException('no rule named "%s"' % name)

        return meta

    @staticmethod
    def all():
        return Rule.REGISTRY.values()

    @classmethod
    def meta(cls):
        split_doc = (cls.__doc__ or '').strip().split('\n', 1)

        return {
            'name': cls.__name__,
            'description': split_doc[0],
            'help': split_doc[1] if len(split_doc) == 2 else None
        }

    def enable(self, ctx):
        raise NotImplementedError('must be overridden by subclass')
