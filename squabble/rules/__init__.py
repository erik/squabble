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
        super().__init_subclass__(**kwargs)
        Registry.register(cls)

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
        """
        Called before the root AST node is traversed. Here's where most
        callbacks should be registered for different AST nodes.

        Each linter is initialized once per file that it is being run
        against. `self._options` will contain the merged base configuration
        with the file-specific configuration options for this linter.
        """
        raise NotImplementedError('must be overridden by subclass')
