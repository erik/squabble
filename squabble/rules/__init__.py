import glob
import importlib
import os.path

from squabble import logger, UnknownRuleException


def load(plugins):
    if plugins != []:
        raise NotImplementedError('no plugin support yet')

    modules = glob.glob(os.path.dirname(__file__) + '/*.py')

    for mod in modules:
        mod_name = os.path.basename(mod)[:-3]

        if not os.path.isfile(mod) or mod_name.startswith('__'):
            continue

        importlib.import_module(__name__ + '.' + mod_name)


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

        logger.debug('registering class %s' % name)

        Rule.REGISTRY[name] = {'class': cls, 'meta': meta}

    @staticmethod
    def get(name):
        meta = Rule.REGISTRY.get(name)
        if meta is None:
            raise UnknownRuleException('no rule named "%s"' % name)

        return meta

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
