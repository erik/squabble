import pglast
from pglast.enums import AlterTableType, ConstrType

from squabble import RuleConfigurationException

from squabble.rules import Rule


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

    Tags: performance, backwards-compatibility
    """

    CONSTRAINT_MAP = {
        'DEFAULT': ConstrType.CONSTR_DEFAULT,
        'NULL': ConstrType.CONSTR_NULL,
        'NOT NULL': ConstrType.CONSTR_NOTNULL,
        'FOREIGN': ConstrType.CONSTR_FOREIGN,
        'UNIQUE': ConstrType.CONSTR_UNIQUE,
    }

    MESSAGES = {
        'constraint_not_allowed': 'column "{col}" has a disallowed constraint'
    }

    def enable(self, ctx):
        disallowed = self._options.get('disallowed', [])
        if disallowed == []:
            raise RuleConfigurationException(self, 'must specify `disallowed` constraints')

        constraints = set()

        for c in disallowed:
            ty = self.CONSTRAINT_MAP[c.upper()]
            if ty is None:
                raise RuleConfigurationException(self, 'unknown constraint: `%s`' % c)

            constraints.add(ty)

        ctx.register('AlterTableCmd', self._check(constraints))

    @Rule.node_visitor
    def _check(self, ctx, node, disallowed_constraints):
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
            if constraint.contype.value in disallowed_constraints:
                col = node['def'].colname.value

                ctx.report(
                    self,
                    'constraint_not_allowed',
                    params={'col': col},
                    node=constraint)
