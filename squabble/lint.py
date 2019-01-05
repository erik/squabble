""" linting engine """

import collections
import enum

import pglast

from squabble.rule import Registry

_LintIssue = collections.namedtuple('_LintIssue', [
    'message',
    'message_text',
    'node',
    'file',
    'severity',
    'location'
])

# Make all the fields nullable
_LintIssue.__new__.__defaults__ = (None,) * len(_LintIssue._fields)


class LintIssue(_LintIssue):
    pass


class Severity(enum.Enum):
    """
    Enumeration describing the relative severity of a :class:`~LintIssue`.

    By themselves, these values don't mean much, but are meant to
    convey the likely hood that a detected issue is truly
    problematic. For example, a syntax error in a migration would be
    ``CRITICAL``, but perhaps a naming inconsistency would be ``LOW``.
    """
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    CRITICAL = 'CRITICAL'


def _parse_string(text):
    """Use ``pglast`` to turn ``text`` into a SQL AST."""
    return pglast.Node(pglast.parse_sql(text))


def _configure_rules(rule_config):
    rules = []

    for name, config in rule_config.items():
        cls = Registry.get_class(name)
        rules.append((cls(), config))

    return rules


def check_file(config, name, contents):
    """
    Return a list of lint issues from using ``config`` to lint
    ``name``.
    """
    rules = _configure_rules(config.rules)
    s = Session(rules, contents, file_name=name)
    return s.lint()


class Session:
    """
    A run of the linter using a given set of rules over a single file. This
    class exists mainly to hold the list of issues returned by the enabled
    rules.
    """
    def __init__(self, rules, sql_text, file_name):
        self._rules = rules
        self._sql = sql_text
        self._issues = []
        self._file_name = file_name

    def report_issue(self, issue):
        i = issue._replace(file=self._file_name)
        self._issues.append(i)

    def lint(self):
        """
        Run the linter on SQL given in constructor, returning a list of
        :class:`~LintIssue` discovered.
        """
        root_ctx = Context(self)

        for rule, config in self._rules:
            rule.enable(root_ctx, config)

        try:
            ast = _parse_string(self._sql)
            root_ctx.traverse(ast)

        except pglast.parser.ParseError as exc:
            root_ctx.report_issue(LintIssue(
                severity=Severity.CRITICAL,
                message_text=exc.args[0],
                location=exc.location
            ))

        return self._issues


class Context:
    """
    Contains the node tag callback hooks enabled at or below the `parent_node`
    passed to the call to `traverse`.

    >>> import pglast
    >>> ast = pglast.Node(pglast.parse_sql('''
    ...   CREATE TABLE foo (id INTEGER PRIMARY KEY);
    ... '''))
    >>> ctx = Context(session=...)
    >>>
    >>> def create_stmt(child_ctx, node):
    ...     print('create stmt')
    ...     child_ctx.register('ColumnDef', lambda _c, _n: print('from child'))
    ...
    >>> ctx.register('CreateStmt', create_stmt)
    >>> ctx.register('ColumnDef', lambda _c, _n: print('from root'))
    >>> ctx.traverse(ast)
    create stmt
    from child
    from root
    """
    def __init__(self, session):
        self._hooks = {}
        self._exit_hooks = []
        self._session = session

    def traverse(self, parent_node):
        """
        Recursively walk down the AST starting at `parent_node`.

        For every node, call any callback functions registered for that
        particular node tag.
        """
        for node in parent_node.traverse():
            # Ignore scalar values
            if not isinstance(node, pglast.node.Node):
                continue

            tag = node.node_tag

            if tag not in self._hooks:
                continue

            child_ctx = Context(self._session)
            for hook in self._hooks[tag]:
                hook(child_ctx, node)

            # children can set up their own hooks, so recurse
            child_ctx.traverse(node)

        for exit_fn in self._exit_hooks:
            exit_fn(self)

    def register_exit(self, fn):
        """
        Register `fn` to be called when the current node is finished being
        traversed.
        """
        self._exit_hooks.append(fn)

    def register(self, node_tag, fn):
        """
        Register `fn` to be called whenever `node_tag` node is visited.

        >>> session = ...
        >>> ctx = Context(session)
        >>> ctx.register('CreateStmt', lambda ctx, node: ...)
        """
        if node_tag not in self._hooks:
            self._hooks[node_tag] = []

        self._hooks[node_tag].append(fn)

    def report_issue(self, issue):
        self._session.report_issue(issue)

    def report(self, message, node=None, severity=None):
        """Convenience wrapper to create and report a lint issue."""
        self.report_issue(LintIssue(
            message=message,
            node=node,
            severity=severity or Severity.MEDIUM,
            # This is filled in later
            file=None,
        ))
