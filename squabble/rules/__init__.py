from squabble.rule import Registry


class BaseRule:
    """
    Base implementation of a linter rule.

    Rules work by adding hooks into the abstract syntax tree for a SQL
    file, and then performing their lint actions inside the callback
    functions.
    """

    def __init__(self, options):
        self._options = options

    def __init_subclass__(cls, **kwargs):
        """Keep track of all classes that inherit from ``BaseRule``."""
        super().__init_subclass__(**kwargs)
        Registry.register(cls)

    @classmethod
    def meta(cls):
        """
        Return metadata about the Rule. Base implementation should be sane
        enough for most purposes.

        >>> class MyRule(BaseRule):
        ...     '''
        ...     Brief description of rule.
        ...
        ...     More details about this rule.
        ...     '''
        >>> m = MyRule.meta()
        >>> m['name']
        'MyRule'
        >>> m['description']
        'Brief description of rule.'
        >>> m['help']
        'More details about this rule.'
        """
        split_doc = (cls.__doc__ or '').strip().split('\n', 1)

        help = None
        if len(split_doc) == 2:
            help = split_doc[1].strip()

        return {
            'name': cls.__name__,
            'description': split_doc[0],
            'help': help
        }

    @classmethod
    def format(cls, message_id, params):
        """
        >>> class MyRule(BaseRule):
        ...     MESSAGES = {'message_1': 'something went {status}'}
        ...
        >>> MyRule.format('message_1', {'status': 'wrong'})
        'something went wrong'
        """
        template = cls.MESSAGES[message_id]
        return template.format(**params)

    @classmethod
    def explain(cls, message_id):
        """
        Provide more context around ``message_id``.

        The purpose of this function is to explain to users _why_ the
        message was raised, and what they can do to resolve the issue.

        The base implementation will look for a function named
        ``explain_{message_id}`` and return the docstring, or None, if
        no such function exists.

        Yeah this is kind of weird.

        >>> class MyRule(BaseRule):
        ...     MESSAGES = {'foo_bar': ...}
        ...
        ...     def explain_foo_bar():
        ...         '''Here is why the rule is relevant...'''
        >>> MyRule.explain('foo_bar')
        'Here is why the rule is relevant...'
        >>> MyRule.explain('baz') is None
        True
        """
        name = 'explain_' + message_id

        if hasattr(cls, name):
            return getattr(cls, name).__doc__

    def enable(self, ctx, config):
        """
        Called before the root AST node is traversed. Here's where most
        callbacks should be registered for different AST nodes.

        Each linter is initialized once per file that it is being run
        against. ``config`` will contain the merged base configuration
        with the file-specific configuration options for this linter.
        """
        raise NotImplementedError('must be overridden by subclass')
