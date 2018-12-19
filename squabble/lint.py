""" linting engine """

import collections

import pglast

from squabble import RuleConfigurationException
from squabble.rules import Rule


LintIssue = collections.namedtuple('LintIssue', [
    'message_id',
    'message_text',
    'message_params',
    'node',
    'file',
    'rule',
    'severity',
    'location'
])

# Make all the fields nullable
LintIssue.__new__.__defaults__ = (None,) * len(LintIssue._fields)


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
    try:
        rules = configure_rules(config.rules)
    except RuleConfigurationException as exc:
        return [LintIssue(
            message_text=exc.msg,
            rule=exc.rule,
            node=None,
            file=file_name,
            severity='ERROR',
            location=None,
        )]

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

        try:
            ast = parse_file(self._file)
            root_ctx.traverse(ast)

        except pglast.parser.ParseError as exc:
            root_ctx.report_issue(LintIssue(
                severity='ERROR',
                message_text=exc.args[0],
                location=exc.location
            ))

        return self._issues


class LintContext:
    def __init__(self, session):
        self._hooks = {}
        self._exit_hooks = []
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

        for exit_fn in self._exit_hooks:
            exit_fn(self)

    def register_exit(self, fn):
        self._exit_hooks.append(fn)

    def register(self, node, fn):
        if node not in self._hooks:
            self._hooks[node] = []

        self._hooks[node].append(fn)

    def report_issue(self, issue):
        self._session.report_issue(issue)

    def report(self, rule, message_id, params=None, node=None, severity='ERROR'):
        self._session.report_issue(LintIssue(
            rule=rule,
            message_id=message_id,
            message_params=params,
            node=node,
            severity=severity,
            # This is filled in later
            file=None,
        ))
