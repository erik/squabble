import inspect

from squabble.rule import Registry


class BaseRule:
    """
    Base implementation of a linter rule.

    Rules work by adding hooks into the abstract syntax tree for a SQL
    file, and then performing their lint actions inside the callback
    functions.

    Rules represent lint issues using pre-defined message classes, which are
    defined by creating a child class inheriting from
    :class:`squabble.message.Message`.

    For example:

    >>> import squabble.message
    >>> class MyRule(BaseRule):
    ...     class BadColumnName(squabble.message.Message):
    ...         TEMPLATE = 'column {name} is not allowed'
    ...
    >>> MyRule.BadColumnName(name='foo').format()
    'column foo is not allowed'
    """

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
        ...     Brief description of rule. This can
        ...     wrap to the next line.
        ...
        ...     More details about this rule.
        ...     '''
        >>> m = MyRule.meta()
        >>> m['name']
        'MyRule'
        >>> m['description']
        'Brief description of rule. This can wrap to the next line.'
        >>> m['help']
        'More details about this rule.'
        """
        split_doc = inspect.cleandoc(cls.__doc__ or '').split('\n\n', 1)

        help = None
        if len(split_doc) == 2:
            help = split_doc[1]

        description = split_doc[0].replace('\n', ' ')

        return {
            'name': cls.__name__,
            'description': description,
            'help': help
        }

    def enable(self, ctx, config):
        """
        Called before the root AST node is traversed. Here's where most
        callbacks should be registered for different AST nodes.

        Each linter is initialized once per file that it is being run
        against. ``config`` will contain the merged base configuration
        with the file-specific configuration options for this linter.
        """
        raise NotImplementedError('must be overridden by subclass')
