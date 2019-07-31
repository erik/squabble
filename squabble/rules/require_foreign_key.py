import re

import pglast
from pglast.enums import AlterTableType, ConstrType

from squabble.message import Message
from squabble.rules import BaseRule


class RequireForeignKey(BaseRule):
    """
    New columns that look like references must have a foreign key constraint.

    By default, "looks like" means that the name of the column matches
    the regex ``.*_id$``, but this is configurable.

    .. code-block:: sql

      CREATE TABLE comments (
        post_id  INT,  -- warning here, this looks like a foreign key,
                       -- but no constraint was given

        -- No warning here
        user_id INT REFERENCES users(id)
      )

      ALTER TABLE books
        ADD COLUMN author_id INT;  -- warning here

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
        fk_regex = re.compile(config.get('column_regex', self._DEFAULT_REGEX))

        # Keep track of column_name -> column_def node so we can
        # report a sane location for the warning when a new column
        # doesn't have a foreign key.
        missing_fk = {}

        # We want to check both columns that are part of CREATE TABLE
        # as well as ALTER TABLE ... ADD COLUMN
        root_ctx.register(
            'CreateStmt',
            lambda _, node: _create_table_stmt(node, fk_regex, missing_fk))

        root_ctx.register(
            'AlterTableStmt',
            lambda _, node: _alter_table_stmt(node, fk_regex, missing_fk))

        def _report_missing(ctx):
            """
            When we exit the root context, any elements remaining in
            ``missing_fk`` are known not to have a FOREIGN KEY
            constraint, so report them as errors.
            """
            for column, node in missing_fk.items():
                ctx.report(
                    self.MissingForeignKeyConstraint(col=column),
                    node=node)

        root_ctx.register_exit(_report_missing)


def _create_table_stmt(table_node, fk_regex, missing_fk):
    table_name = table_node.relation.relname.value
    if table_node.tableElts == pglast.Missing:
        return

    for e in table_node.tableElts:
        # Defining a column, may include an inline constraint.
        if e.node_tag == 'ColumnDef':
            if _column_needs_foreign_key(fk_regex, e):
                key = '{}.{}'.format(table_name, e.colname.value)
                missing_fk[key] = e

        # FOREIGN KEY (...) REFERENCES ...
        elif e.node_tag == 'Constraint':
            _remove_satisfied_foreign_keys(e, table_name, missing_fk)


def _alter_table_stmt(node, fk_regex, missing_fk):
    table_name = node.relation.relname.value

    for cmd in node.cmds:
        if cmd.subtype == AlterTableType.AT_AddColumn:
            if _column_needs_foreign_key(fk_regex, cmd['def']):
                key = '{}.{}'.format(table_name, cmd['def'].colname.value)
                missing_fk[key] = cmd['def']

        elif cmd.subtype in (AlterTableType.AT_AddConstraint,
                             AlterTableType.AT_AddConstraintRecurse):
            constraint = cmd['def']
            _remove_satisfied_foreign_keys(constraint, table_name, missing_fk)


def _remove_satisfied_foreign_keys(constraint, table_name, missing_fk):
    # Nothing to do if this isn't a foreign key constraint
    if constraint.contype != ConstrType.CONSTR_FOREIGN:
        return

    # Clear out any columns that we earlier identified as
    # needing a foreign key.
    for col_name in constraint.fk_attrs:
        key = '{}.{}'.format(table_name, col_name.string_value)
        missing_fk.pop(key, '')


def _column_needs_foreign_key(fk_regex, column_def):
    """
    Return True if the ``ColumnDef`` defines a column with a name that
    matches the foreign key regex but does not specify an inline
    constraint.

    >>> import re
    >>> import pglast

    >>> fk_regex = re.compile('.*_id$')
    >>> cols = {
    ...     # name doesn't match regex
    ...     'email': {'ColumnDef': {'colname': 'email'}},
    ...
    ...     # name matches regex, but no foreign key
    ...     'users_id': {'ColumnDef': {'colname': 'users_id'}},
    ...
    ...     # name matches regex, but has foreign key (contype == 8)
    ...     'post_id': {'ColumnDef': {
    ...         'colname': 'post_id',
    ...         'constraints': [{'Constraint': {'contype': 8}}]
    ...      }}
    ... }
    >>> _column_needs_foreign_key(fk_regex, pglast.Node(cols['email']))
    False
    >>> _column_needs_foreign_key(fk_regex, pglast.Node(cols['users_id']))
    True
    >>> _column_needs_foreign_key(fk_regex, pglast.Node(cols['post_id']))
    False
    """
    name = column_def.colname.value
    if not fk_regex.match(name):
        return False

    if column_def.constraints == pglast.Missing:
        return True

    return not any(
        e.contype == ConstrType.CONSTR_FOREIGN
        for e in column_def.constraints
    )
