import functools
import glob
import importlib
import importlib.util as import_util
import logging
import os.path

from squabble import UnknownRuleException


logger = logging.getLogger(__name__)


def _load_plugin(path):
    """
    Given an arbitrary directory, try to load all Python files in order
    to register the custom rule definitions.

    Nothing is done with the Python files once they're loaded, it is
    assumed that simply importing the module will be enough to have the
    side effect of registering the modules correctly.
    """
    logger.debug('trying to load "%s" as a plugin directory', path)

    if not os.path.isdir(path):
        raise NotADirectoryError('cannot load "%s": not a directory' % path)

    files = os.path.join(path, '*.py')
    pkg_name = os.path.basename(os.path.dirname(path))

    for file_name in glob.glob(files):
        logger.debug('loading file "%s" to pkg "%s"', file_name, pkg_name)
        spec = import_util.spec_from_file_location(pkg_name, file_name)

        # Parse and execute the file
        mod = import_util.module_from_spec(spec)
        spec.loader.exec_module(mod)


def _load_builtin_rules():
    """Load the rules that ship with squabble (squabble/rules/*.py)"""
    modules = glob.glob(os.path.dirname(__file__) + '/rules/*.py')

    # Sort the modules to guarantee stable ordering
    for mod in sorted(modules):
        mod_name = os.path.basename(mod)[:-3]

        if not os.path.isfile(mod) or mod_name.startswith('__'):
            continue

        importlib.import_module('squabble.rules.' + mod_name)


def load_rules(plugin_paths=None):
    """
    Load built in rules as well as any custom rules contained in the
    directories in `plugin_paths`.
    """
    _load_builtin_rules()

    # Import plugins last so their naming takes precedence
    plugin_paths = plugin_paths or []
    for path in plugin_paths:
        _load_plugin(path)


def node_visitor(fn):
    """
    Helper decorator to make it easier to register callbacks for AST
    nodes. Effectively creates the partial function automatically so
    there's no need for a lambda.

    Wraps ``fn`` to pass in ``self``, ``context``, and ``node``
    when the callback is called.

    >>> from squabble.rules import BaseRule
    >>> class SomeRule(BaseRule):
    ...     def enable(self, ctx, config):
    ...         # These are equivalent
    ...         ctx.register('foo', self.check_foo(x=1))
    ...         ctx.register('bar', lambda c, n: self.check_bar(c, n, x=1))
    ...
    ...     @node_visitor
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


class Registry:
    """
    Singleton instance used to keep track of all rules.

    Any class that inherits from :class:`squabble.rules.BaseRule` will
    automatically be registered to the registry.
    """
    _REGISTRY = {}

    @staticmethod
    def register(rule):
        meta = rule.meta()
        name = meta['name']

        logger.debug('registering rule "%s"', name)

        Registry._REGISTRY[name] = {'class': rule, 'meta': meta}

    @staticmethod
    def get_meta(name):
        """
        Return metadata about a given rule in the registry.

        If no rule exists in the registry named ``name``,
        :class:`UnknownRuleException` will be thrown.

        The returned dictionary will look something like this:

        .. code-block:: python

            {
                'name': 'RuleClass',
                'help': 'Some rule...',
                # ...
            }
        """
        if name not in Registry._REGISTRY:
            raise UnknownRuleException(name)

        return Registry._REGISTRY[name]['meta']

    @staticmethod
    def get_class(name):
        """
        Return class for given rule name in the registry.

        If no rule exists in the registry named ``name``,
        :class:`UnknownRuleException` will be thrown.
        """
        if name not in Registry._REGISTRY:
            raise UnknownRuleException(name)

        return Registry._REGISTRY[name]['class']

    @staticmethod
    def all():
        """
        Return an iterator over all known rule metadata. Equivalent to calling
        :func:`~Registry.get_meta()` for all registered rules.
        """
        for r in Registry._REGISTRY.values():
            yield r['meta']
