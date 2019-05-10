import inspect
import logging

from squabble import SquabbleException


logger = logging.getLogger(__name__)


class DuplicateMessageCodeException(SquabbleException):
    def __init__(self, dupe):
        original = Registry.by_code(dupe.CODE)
        message = 'Message %s has the same code as %s' % (dupe, original)

        super().__init__(message)


class Registry:
    """
    Singleton which maps message code values to classes.

    >>> class MyMessage(Message):
    ...     '''My example message.'''
    ...     TEMPLATE = '...'
    ...     CODE = 5678
    >>> cls = Registry.by_code(5678)
    >>> cls.explain()
    'My example message.'
    >>> cls is MyMessage
    True

    Duplicate codes are not allowed, and will throw an exception.

    >>> class MyDuplicateMessage(Message):
    ...     CODE = 5678
    Traceback (most recent call last):
      ...
    squabble.message.DuplicateMessageCodeException: ...
    """

    _MAP = {}
    _CODE_COUNTER = 9000

    @classmethod
    def register(cls, msg):
        """
        Add ``msg`` to the registry, and assign a ``CODE`` value if not
        explicitly specified.
        """
        if msg.CODE is None:
            setattr(msg, 'CODE', cls._next_code())
            logger.info('assigning code %s to %s', msg.CODE, msg)

        # Don't allow duplicates
        if msg.CODE in cls._MAP:
            raise DuplicateMessageCodeException(msg)

        cls._MAP[msg.CODE] = msg

    @classmethod
    def by_code(cls, code):
        """
        Return the :class:`squabble.message.Message` class identified by
        ``code``, raising a :class:`KeyError` if it doesn't exist.
        """
        return cls._MAP[code]

    @classmethod
    def _next_code(cls):
        cls._CODE_COUNTER += 1
        return cls._CODE_COUNTER


class Message:
    """
    Messages represent specific issues identified by a lint rule.

    Each class that inherits from ``Message`` should have a docstring
    which explains the reasoning and context of the message, as well
    as a class member variable named ``TEMPLATE``, which is used to
    display a brief explanation on the command line.

    Messages may also have a ``CODE`` class member, which is used to
    identify the message. The actual value doesn't matter much, as
    long as it is unique among all the loaded ``Message`` s. If no
    ``CODE`` is defined, one will be assigned.

    >>> class TooManyColumns(Message):
    ...    '''
    ...    This may indicate poor design, consider multiple tables instead.
    ...    '''
    ...    TEMPLATE = 'table "{table}" has > {limit} columns'
    ...    CODE = 1234
    >>> message = TooManyColumns(table='foo', limit=30)
    >>> message.format()
    'table "foo" has > 30 columns'
    >>> message.explain()
    'This may indicate poor design, consider multiple tables instead.'
    """
    TEMPLATE = None
    CODE = None

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __init_subclass__(cls, **kwargs):
        """Assign unique (locally, not globally) message codes."""
        super().__init_subclass__(**kwargs)
        Registry.register(cls)

    def format(self):
        return self.TEMPLATE.format(**self.kwargs)

    @classmethod
    def explain(cls):
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
        if not cls.__doc__:
            return None

        # Remove the leading indentation on the docstring
        return inspect.cleandoc(cls.__doc__)

    def asdict(self):
        """
        Return dictionary representation of message, for formatting.

        >>> class SummaryMessage(Message):
        ...     CODE = 90291
        ...     TEMPLATE = 'everything is {status}'
        ...
        >>> msg = SummaryMessage(status='wrong')
        >>> msg.asdict() == {
        ...   'message_id': 'SummaryMessage',
        ...   'message_text': 'everything is wrong',
        ...   'message_template': SummaryMessage.TEMPLATE,
        ...   'message_params': {'status': 'wrong'},
        ...   'message_code': 90291
        ... }
        True
        """
        return {
            'message_id': self.__class__.__name__,
            'message_text': self.format(),
            'message_template': self.TEMPLATE,
            'message_params': self.kwargs,
            'message_code': self.CODE
        }
