import re

import pglast
from pglast.enums import ConstrType

import squabble.rule
from squabble.lint import Severity
from squabble.message import Message
from squabble.rules import BaseRule


class RequireForeignKey(BaseRule):
    """
    New columns that look like references have a foreign key constraint.

    By default, "look like" means that the name of the column matches
    the regex ``.*_id$``, but this is configurable.

    Configuration ::

      {
          "RequireForeignKey": {
              "column_regex": ".*_id$"
          }
      }
    """

    class MissingForeignKeyConstraint(Message):
        """
        Foreign keys are a good way to guarantee that your database
        retains referential integrity.

        When adding a new column that points to another table, make sure to add
        a constraint so that the database can check that it points to a valid
        record.

        Foreign keys can either be added when creating a table, or
        after the fact in the case of adding a new column.

        .. code-block:: sql

          -- Each of these forms is acceptable:
          CREATE TABLE admins (user_id INTEGER REFERENCES users(id));

          CREATE TABLE admins (
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
          );

          ALTER TABLE admins ADD COLUMN user_id INTEGER REFERENCES users(id);

          ALTER TABLE admins ADD FOREIGN KEY user_id REFERENCES users(id);
        """
        TEMPLATE = '"{col}" may need a foreign key constraint'
        CODE = 1008

    _DEFAULT_REGEX = '.*_id$'

    def enable(self, root_ctx, config):
        column_re = re.compile(config.get('column_regex', self._DEFAULT_REGEX))
        columns = {}

        # We want to check both columns that are part of CREATE TABLE s
        root_ctx.register('CreateStmt', self._create_table(column_re, columns))
        root_ctx.register('AlterTableStmt', self._alter_table(column_re, columns))

        def _report_missing(ctx):
            nonlocal columns

            for column, node in columns.items():
                print('reporting missing:', column)
                ctx.report(
                    self.MissingForeignKeyConstraint(col=column),
                    node=node)

        root_ctx.register_exit(_report_missing)

    @squabble.rule.node_visitor
    def _create_table(self, ctx, table_node, column_re, columns):
        def _has_fk(constraints):
            if constraints == pglast.Missing:
                return False

            return any(
                e.contype == ConstrType.CONSTR_FOREIGN
                for e in constraints
            )

        table_name = table_node.relation.relname.value
        missing_fk = {}

        for e in table_node.tableElts:
            # Defining a column, may include an inline constraint.
            if e.node_tag == 'ColumnDef':
                col_name = e.colname.value
                if column_re.match(col_name) and not _has_fk(e.constraints):
                    missing_fk[col_name] = e

            # FOREIGN KEY (...) REFERENCES ...
            elif e.node_tag == 'Constraint':
                if e.contype != ConstrType.CONSTR_FOREIGN:
                    continue

                # Clear out any columns that we earlier identified as
                # needing a foreign key.
                for col_name in e.fk_attrs:
                    missing_fk.pop(col_name.string_value, '')

        for column, node in missing_fk.items():
            key = '{}.{}'.format(table_name, column)
            columns[key] = node

    @squabble.rule.node_visitor
    def _alter_table(self, ctx, node, column_re, columns):
        # TODO: write this part
        pass
