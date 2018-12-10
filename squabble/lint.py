""" linting engine """


class Engine:
    def __init__(self, rules):
        self._rules = rules
        self._stack = []

    @staticmethod
    def from_config(config, enabled_rules):
        engine = Engine(enabled_rules)

        return engine

    def lint(self, file_name):
        pass


def LintContext:
    def __init__(self):
        pass
