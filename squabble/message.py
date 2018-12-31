import re


class Message:
    """
    Messages represent specific issues identified by a lint rule.

    Each class that inherits from ``Message`` should have a docstring
    which explains the reasoning and context of the message, as well
    as a class member variable named ``TEMPLATE``, which is used to
    display a brief explanation on the command line.

    >>> class TooManyColumns(Message):
    ...    '''
    ...    This may indicate poor design, consider multiple tables instead.
    ...    '''
    ...    TEMPLATE = 'table "{table}" has > {limit} columns'
    >>> message = TooManyColumns(table='foo', limit=30)
    >>> message.format()
    'table "foo" has > 30 columns'
    >>> message.explain()
    'This may indicate poor design, consider multiple tables instead.'
    """
    TEMPLATE = None

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def format(self):
        return self.TEMPLATE.format(**self.kwargs)

    def explain(self):
        """
        Provide more context around this message.

        The purpose of this function is to explain to users _why_ the
        message was raised, and what they can do to resolve the issue.

        The base implementation will simply return the docstring for
        the class, but this can be overridden if more specialized
        behavior is necessary.

        >>> class NoDocString(Message): pass
        >>> NoDocString().explain() is None
        True
        """
        if not self.__doc__:
            return None

        return self.__doc__.strip()

    def asdict(self):
        name = self.__class__.__name__
        snake_name = re.sub('(?!^)([A-Z]+)', r'_\1', name).lower()

        return {
            'message_id': snake_name,
            'message_text': self.format(),
            'message_template': self.TEMPLATE,
            'message_params': self.kwargs,
        }
