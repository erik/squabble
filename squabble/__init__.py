import abc
import sys
import types
import logging


logger = logging.getLogger(__name__)


class SquabbleException(Exception):
    """Base exception type for all things in this package"""


class RuleConfigurationException(SquabbleException):
    def __init__(self, rule, msg):
        self.rule = rule
        self.msg = msg


class UnknownRuleException(SquabbleException):
    def __init__(self, name):
        super().__init__('unknown rule: "%s"' % name)


HAS_PY36 = sys.version_info >= (3, 6)
HAS_PEP487 = HAS_PY36

if HAS_PEP487:
    PEP487Meta = type         # pragma: no cover
    PEP487Base = object       # pragma: no cover
    PEP487Object = object     # pragma: no cover
else:
    class PEP487Meta(type):
        def __new__(mcls, name, bases, ns, **kwargs):
            init = ns.get('__init_subclass__')
            if isinstance(init, types.FunctionType):
                ns['__init_subclass__'] = classmethod(init)
            cls = super().__new__(mcls, name, bases, ns)
            for key, value in cls.__dict__.items():
                func = getattr(value, '__set_name__', None)
                if func is not None:
                    func(cls, key)
            super(cls, cls).__init_subclass__(**kwargs)
            return cls

        def __init__(cls, name, bases, ns, **kwargs):
            super().__init__(name, bases, ns)

    class PEP487Base:
        @classmethod
        def __init_subclass__(cls, **kwargs):
            pass

    class PEP487Object(PEP487Base, metaclass=PEP487Meta):
        pass
