import functools
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


def _load_builtin_rules():
    """Load the rules that ship with squabble (squabble/rules/*.py)"""
    modules = glob.glob(os.path.dirname(__file__) + '/*.py')

    for mod in modules:
        mod_name = os.path.basename(mod)[:-3]

        if not os.path.isfile(mod) or mod_name.startswith('__'):
            continue

        importlib.import_module(__name__ + '.' + mod_name)


def load(plugin_paths=[]):
    """
    Load built in rules as well as any custom rules contained in the
    directories in `plugin_paths`.
    """

    _load_builtin_rules()

    # Import plugins last so their naming takes precedence
    for path in plugin_paths:
        _load_plugin(path)


class Registry:
    """Singleton instance used to keep track of all rules"""
    _REGISTRY = {}

    @staticmethod
    def register(rule):
        meta = rule.meta()
        name = meta['name']

        logger.debug('registering rule "%s"', name)

        Registry._REGISTRY[name] = {'class': rule, 'meta': meta}

    @staticmethod
    def get_meta(name):
        """Return metadata about a given rule in the registry"""
        if name not in Registry._REGISTRY:
            raise UnknownRuleException(name)

        return Registry._REGISTRY[name]

    @staticmethod
    def all():
        """
        Return an iterator over all known Rule metadata. Equivalent to calling
        `Registry.get(name)` for all registered rules.
        """
        return Registry._REGISTRY.values()


class Rule:
    def __init__(self, options):
        self._options = options

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Registry.register(cls)

    @staticmethod
    def node_visitor(fn):
        """
        Helper decorator to make it easier to register callbacks for AST
        nodes. Effectively creates the partial function automatically so
        there's no need for a lambda.

        Wraps `fn` to pass in `self`, `context`, and `node` when the callback
        is called.

        >>> class SomeRule(Rule):
        ...     def enable(ctx):
        ...         # These are equivalent
        ...         ctx.register('foo', self.check_foo(x=1))
        ...         ctx.register('bar', lambda c, n: self.check_bar(c, n, x=1))
        ...
        ...     @Rule.node_visitor
        ...     def check_foo(self, context, node, x):
        ...         pass
        ...
        ...     def check_bar(self, context, node, x):
        ...         pass
        """

        def wrapper(self, *args, **kwargs):
            @functools.wraps(fn)
            def inner(context, node):
                return fn(self, context, node, *args, **kwargs)
            return inner

        return wrapper

    @classmethod
    def meta(cls):
        """
        Return metadata about the Rule. Base implementation should be sane
        enough for most purposes.
        """
        split_doc = (cls.__doc__ or '').strip().split('\n', 1)

        return {
            'name': cls.__name__,
            'description': split_doc[0],
            'help': split_doc[1] if len(split_doc) == 2 else None
        }

    def enable(self, ctx):
        raise NotImplementedError('must be overridden by subclass')
