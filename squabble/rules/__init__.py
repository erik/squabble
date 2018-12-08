from functools import wraps


class Rule:
    def __init__(self):
        self._nodes = []

    def on_node(self, path, callback):
        print(path, callback)
        self._nodes.append((path, callback))

    def register(*paths):
        print('paths', paths)

        def wrapper(fn):
            print('fun', fn)
            for p in paths:
                print('ON NODE', p)
                self.on_node(p, fn)

            @wraps(fn)
            def inner(self, *args, **kwargs):
                return fn(self, *args, **kwargs)
            return inner

        return wrapper


class AddColumnNoDefaults(Rule):
    """Prevent adding a column with a default value to an existing table"""

    @Rule.register(['AlterTableStmt', 'AlterTableCmd'])
    def check(self, node):
        pass


def load():
    return [
        AddColumnNoDefaults
    ]
