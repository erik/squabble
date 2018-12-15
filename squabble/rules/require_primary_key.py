import pglast
from pglast.enums import ConstrType

from squabble.rules import Rule


class RequirePrimaryKey(Rule):
    """
    Require that all new tables specify a PRIMARY KEY constraint.

    Configuration:

        "rules": {
            "RequirePrimaryKey": {}
        }
    """

    MESSAGES = {
        'missing_primary_key': 'table "{0}" does not name a primary key'
    }

    def __init__(self, opts):
        self._opts = opts
        self._table = None
        self._seen_pk = False

    def enable(self, ctx):
        ctx.register('CreateStmt', lambda c, n: self._create_table(c, n))

    def _create_table(self, ctx, node):
        self._table = node
        self._seen_pk = False

        def _check_constraint(_ctx, constraint):
            if constraint.contype == ConstrType.CONSTR_PRIMARY:
                self._seen_pk = True

        def _check_column(_ctx, col):
            if col.constraints == pglast.Missing:
                return

            for c in col.constraints:
                _check_constraint(_ctx, c)

        ctx.register('ColumnDef', _check_column)
        ctx.register('Constraint', _check_constraint)

        ctx.register_exit(lambda c: self._check_pk(c))

    def _check_pk(self, ctx):
        """
        Make sure we've seen a primary key constraint by the time the
        `CREATE TABLE` statement is finished.
        """

        if self._seen_pk:
            return

        # Use the table's name as the reported error's location
        node = self._table.relation
        table_name = node.relname.value

        msg = self.MESSAGES['missing_primary_key'].format(table_name)

        ctx.report(self, msg, node=node)
