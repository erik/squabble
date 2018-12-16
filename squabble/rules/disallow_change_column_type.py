from pglast.enums import AlterTableType

from squabble.rules import Rule


class DisallowChangeColumnType(Rule):
    """
    Prevent changing the type of an existing column.

    Configuration:

        "rules": {
            "DisallowChangeColumnType": {}
        }
    """

    MESSAGES = {
        'change_type_not_allowed': ('cannot change type of existing column '
                                    '"{col}"')
    }

    def __init__(self, opts):
        self._opts = opts

    def enable(self, ctx):
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
