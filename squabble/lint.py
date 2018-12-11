""" linting engine """

import collections

import pglast

from .rules import Rule


LintIssue = collections.namedtuple('LintIssue', [
    'msg',
    'verbose',
    'node',
    'file',
    'rule',
    'severity',
])


def parse_file(file_name):
    with open(file_name, 'r') as fp:
        contents = fp.read()

    return pglast.Node(pglast.parse_sql(contents))


def configure_rules(rule_config):
    rules = []

    for name, options in rule_config.items():
        meta = Rule.get(name)
        cls = meta['class']

        rules.append(cls(options))

    return rules


def check_file(config, file_name):
    rules = configure_rules(config.rules)

    s = Session(rules, file_name)
    return s.lint()


class Session:
    def __init__(self, rules, file_name):
        self._rules = rules
        self._file = file_name
        self._issues = []

    def report_issue(self, issue):
        i = issue._replace(file=self._file)
        self._issues.append(i)

    def lint(self):
        root_ctx = LintContext(self)

        for rule in self._rules:
            rule.enable(root_ctx)

        ast = parse_file(self._file)
        root_ctx.traverse(ast)

        return self._issues


class LintContext:
    def __init__(self, session):
        self._hooks = {}
        self._session = session

    def traverse(self, parent_node):
        for node in parent_node.traverse():
            # Ignore scalar values
            if not isinstance(node, pglast.node.Node):
                continue

            tag = node.node_tag
            for hook in self._hooks.get(tag, []):
                child_ctx = LintContext(self._session)
                hook(child_ctx, node)

                # children can set up their own hooks, so recurse
                child_ctx.traverse(node)

    def register(self, nodes, fn):
        """TODO: write me"""
        for n in nodes:
            if n not in self._hooks:
                self._hooks[n] = []

            self._hooks[n].append(fn)

    def report(self, rule, msg, node, verbose=None, severity='ERROR'):
        self._session.report_issue(LintIssue(
            rule=rule,
            msg=msg,
            node=node,
            verbose=verbose,
            severity=severity,
            file=None
        ))
