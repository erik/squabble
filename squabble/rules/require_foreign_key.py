import re

import pglast
from pglast.enums import AlterTableType, ConstrType

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

        # Keep track of column_name -> column_def node so we can
        # report a sane location for the warning when a new column
        # doesn't have a foreign key.
        missing_fk = {}

        # We want to check both columns that are part of CREATE TABLE
        # as well as ALTER TABLE ... ADD COLUMN
        root_ctx.register(
            'CreateStmt',
            lambda _, node: _create_table_stmt(node, column_re, missing_fk))

        root_ctx.register(
            'AlterTableStmt',
            lambda _, node: _alter_table_stmt(node, column_re, missing_fk))

        def _report_missing(ctx):
            nonlocal missing_fk

            for column, node in missing_fk.items():
                ctx.report(
                    self.MissingForeignKeyConstraint(col=column),
                    node=node)

        root_ctx.register_exit(_report_missing)


def _create_table_stmt(table_node, column_re, missing_fk):
    table_name = table_node.relation.relname.value

    for e in table_node.tableElts:
        # Defining a column, may include an inline constraint.
        if e.node_tag == 'ColumnDef':
            if _column_needs_foreign_key(column_re, e):
                key = '{}.{}'.format(table_name, e.colname.value)
                missing_fk[key] = e

        # FOREIGN KEY (...) REFERENCES ...
        elif e.node_tag == 'Constraint':
            _remove_satisfied_foreign_keys(table_name, e, missing_fk)


def _alter_table_stmt(node, column_re, missing_fk):
    table_name = node.relation.relname.value

    for cmd in node.cmds:
        if cmd.subtype == AlterTableType.AT_AddColumn:
            col_name = cmd['def'].colname.value
            if _column_needs_foreign_key(column_re, cmd['def']):
                key = '{}.{}'.format(table_name, col_name)
                missing_fk[key] = cmd['def']

        elif cmd.subtype in (AlterTableType.AT_AddConstraint,
                             AlterTableType.AT_AddConstraintRecurse):
            constraint = cmd['def']
            _remove_satisfied_foreign_keys(table_name, constraint, missing_fk)


def _remove_satisfied_foreign_keys(table_name, constraint, missing_fk):
    # Nothing to do if this isn't a foreign key constraint
    if constraint.contype != ConstrType.CONSTR_FOREIGN:
        return

    # Clear out any columns that we earlier identified as
    # needing a foreign key.
    for col_name in constraint.fk_attrs:
        key = '{}.{}'.format(table_name, col_name.string_value)
        missing_fk.pop(key, '')


def _column_needs_foreign_key(column_re, column_def):
    name = column_def.colname.value
    if not column_re.match(name):
        return False

    if column_def.constraints == pglast.Missing:
        return True

    return not any(
        e.contype == ConstrType.CONSTR_FOREIGN
        for e in column_def.constraints
    )
