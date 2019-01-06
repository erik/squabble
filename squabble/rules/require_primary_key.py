import pglast
from pglast.enums import ConstrType

import squabble.rule
from squabble.message import Message
from squabble.rules import BaseRule


class RequirePrimaryKey(BaseRule):
    """
    Require that all new tables specify a ``PRIMARY KEY`` constraint.

    Configuration: ::

        { "RequirePrimaryKey": {} }
    """

    class MissingPrimaryKey(Message):
        """
        When creating a new table, it's usually a good idea to define a primary
        key, as it can guarantee a unique, fast lookup into the table.

        If no single column will uniquely identify a row, creating a composite
        primary key is also possible.

        .. code-block:: sql

          CREATE TABLE users (email VARCHAR(128) PRIMARY KEY);

          -- Also valid
          CREATE TABLE users (
            email VARCHAR(128),
            -- ...
            PRIMARY KEY(email)
          );
        """
        CODE = 1002
        TEMPLATE = 'table "{tbl}" does not name a primary key'

    def enable(self, ctx, _config):
        ctx.register('CreateStmt', self._create_table())

    @squabble.rule.node_visitor
    def _create_table(self, ctx, node):
        seen_pk = False

        def _check_constraint(_ctx, constraint):
            nonlocal seen_pk

            if constraint.contype == ConstrType.CONSTR_PRIMARY:
                seen_pk = True

        def _check_column(_ctx, col):
            if col.constraints == pglast.Missing:
                return

            for c in col.constraints:
                _check_constraint(_ctx, c)

        ctx.register('ColumnDef', _check_column)
        ctx.register('Constraint', _check_constraint)

        ctx.register_exit(lambda c: self._check_pk(c, seen_pk, node))

    def _check_pk(self, ctx, seen_pk, table_node):
        """
        Make sure we've seen a primary key constraint by the time the
        `CREATE TABLE` statement is finished.
        """
        if seen_pk:
            return

        # Use the table's name as the reported error's location
        node = table_node.relation

        ctx.report(self.MissingPrimaryKey(tbl=node.relname.value),
                   node=node)
