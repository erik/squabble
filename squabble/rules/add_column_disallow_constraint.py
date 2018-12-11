import pglast
from pglast.enums import AlterTableType, ConstrType

from .. import RuleConfigurationException

from . import Rule


class AddColumnDisallowConstraints(Rule):
    """
    Prevent adding a column with certain constraints to an existing table

    Configuration:

        "rules": {
            "AddColumnDisallowConstraints": {
                "disallowed": ["DEFAULT", "FOREIGN"]
            }
        }

    Valid constraint types:
      - DEFAULT
      - NULL
      - NOT NULL
      - FOREIGN
      - UNIQUE
    """

    CONSTRAINT_MAP = {
        'DEFAULT': ConstrType.CONSTR_DEFAULT,
        'NULL': ConstrType.CONSTR_NULL,
        'NOT NULL': ConstrType.CONSTR_NOTNULL,
        'FOREIGN': ConstrType.CONSTR_FOREIGN,
        'UNIQUE': ConstrType.CONSTR_UNIQUE,
    }

    MESSAGES = {
        'constraint_not_allowed': 'column "{0}" has a disallowed constraint'
    }

    def __init__(self, opts):
        if 'disallowed' not in opts or opts['disallowed'] == []:
            raise RuleConfigurationException(
                'must specify `disallowed` constraints')

        constraints = []

        for c in opts['disallowed']:
            ty = self.CONSTRAINT_MAP[c.upper()]
            if ty is None:
                raise RuleConfigurationException('unknown constraint: `%s`' % c)

            constraints.append(ty)

        self._opts = opts
        self._blocked_constraints = set(constraints)

    def enable(self, ctx):
        ctx.register(['AlterTableCmd'], lambda c, n: self.check(c, n))

    def check(self, ctx, node):
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

        # We only care about adding a column
        if node.subtype != AlterTableType.AT_AddColumn:
            return

        constraints = node['def'].constraints

        # No constraints imposed, nothing to do.
        if constraints == pglast.Missing:
            return

        for constraint in constraints:
            if constraint.contype.value in self._blocked_constraints:
                col = node['def'].colname.value
                msg = self.MESSAGES['constraint_not_allowed'].format(col)

                ctx.failure(msg, node=constraint)
