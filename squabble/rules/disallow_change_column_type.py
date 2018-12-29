from pglast.enums import AlterTableType

from squabble.rules import BaseRule


class DisallowChangeColumnType(BaseRule):
    """
    Prevent changing the type of an existing column.

    Configuration:

    .. code-block:: json

       { "DisallowChangeColumnType": {} }

    Tags: backwards-compatibility
    """

    MESSAGES = {
        'change_type_not_allowed': ('cannot change type of existing column '
                                    '"{col}"')
    }

    def __init__(self, opts):
        self._opts = opts

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

        ctx.report(
            self,
            'change_type_not_allowed',
            params={'col': node.name.value},
            node=ty)
