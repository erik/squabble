from pglast.enums import AlterTableType

from squabble.message import Message
from squabble.rules import BaseRule


class DisallowChangeColumnType(BaseRule):
    """
    Prevent changing the type of an existing column.

    Configuration: ::

       { "DisallowChangeColumnType": {} }
    """

    class ChangeTypeNotAllowed(Message):
        """
        Trying to change the type of an existing column may hold a
        full table lock while all of the rows are modified.

        Additionally, changing the type of a column may not be
        backwards compatible with code that has already been deployed.

        Instead, try adding a new column with the updated type, and
        then migrate over.

        For example, to migrate a column from ``type_a`` to ``type_b``.

        .. code-block:: sql

           ALTER TABLE foo ADD COLUMN bar_new type_b;
           UPDATE foo SET bar_new = cast(bar_old, type_b);
           -- Deploy server code to point to new column
           ALTER TABLE foo DROP COLUMN bar_old;
        """
        CODE = 1003
        TEMPLATE = 'cannot change type of existing column "{col}"'

    def enable(self, ctx, _config):
        ctx.register('AlterTableCmd', lambda c, n: self._check(c, n))

    def _check(self, ctx, node):
        """
        Node is an `AlterTableCmd`:

        {
          'AlterTableCmd': {
            'def': {
              'ColumnDef': {
                'colname': 'bar',
                'constraints': [{'Constraint': {'contype': 2, 'location': 35}}]
              }
            }
          }
        }
        """

        # We only care about changing the type of a column
        if node.subtype != AlterTableType.AT_AlterColumnType:
            return

        ty = node['def'].typeName

        issue = self.ChangeTypeNotAllowed(col=node.name.value)
        ctx.report(issue, node=ty)
