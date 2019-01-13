from pglast.enums import ConstrType

import squabble
from squabble.message import Message
from squabble.rules import BaseRule


class DisallowForeignKey(BaseRule):
    """
    Prevent creation of new ``FOREIGN KEY`` constraints.

    Optionally, can be configured with a list of table names that ARE
    allowed to create foreign key references.

    This rule will check ``CREATE TABLE`` and ``ALTER TABLE``
    statements for foreign keys.

    Configuration ::

      {
          "DisallowForeignKey": {
              "excluded": ["table1", "table2"]
          }
      }
    """

    class DisallowedForeignKeyConstraint(Message):
        """
        Sometimes, foreign keys are not possible, or may cause more
        overhead than acceptable.

        If you're working with multiple services, each of which with
        their own database, it's not possible to create a foreign key
        reference to a table that exists on another database. In this
        case, you'll likely need to rely on your business logic being
        correct to guarantee referential integrity.

        A foreign key constraint requires the database to query the
        referenced table to ensure that the value exists. On
        high-traffic, write heavy production instances, this may cause
        unacceptable overhead on writes.
        """
        TEMPLATE = '"{table}" has disallowed foreign key constraint'
        CODE = 1009

    def enable(self, root_ctx, config):
        allowed_tables = set(
            name.lower()
            for name in config.get('excluded', [])
        )

        # We want to check both columns that are part of CREATE TABLE
        # as well as ALTER TABLE ... ADD COLUMN
        root_ctx.register(
            'CreateStmt', self._check_for_foreign_key(allowed_tables))

        root_ctx.register(
            'AlterTableStmt', self._check_for_foreign_key(allowed_tables))

    @squabble.rule.node_visitor
    def _check_for_foreign_key(self, ctx, node, allowed_tables):
        """
        Make sure ``node`` doesn't have a FOREIGN KEY reference.

        Coincidentally, both ``AlterTableStmt`` and ``CreateStmt``
        have a similar enough structure that we can use the same
        function for both.
        """
        table_name = node.relation.relname.value.lower()

        # No need to check further after this
        if table_name in allowed_tables:
            return

        def _check_constraint(child_ctx, constraint):
            if constraint.contype == ConstrType.CONSTR_FOREIGN:
                child_ctx.report(
                    self.DisallowedForeignKeyConstraint(table=table_name),
                    node=constraint
                )

        ctx.register('Constraint', _check_constraint)
