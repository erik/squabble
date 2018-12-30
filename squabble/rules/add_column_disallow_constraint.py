import pglast
from pglast.enums import AlterTableType, ConstrType

import squabble.rule
from squabble import RuleConfigurationException
from squabble.rules import BaseRule


class AddColumnDisallowConstraints(BaseRule):
    """
    Prevent adding a column with certain constraints to an existing table

    Configuration:

    .. code-block:: json

       {
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

    _CONSTRAINT_MAP = {
        'DEFAULT': ConstrType.CONSTR_DEFAULT,
        'NULL': ConstrType.CONSTR_NULL,
        'NOT NULL': ConstrType.CONSTR_NOTNULL,
        'FOREIGN': ConstrType.CONSTR_FOREIGN,
        'UNIQUE': ConstrType.CONSTR_UNIQUE,
    }

    MESSAGES = {
        'constraint_not_allowed': 'column "{col}" has a disallowed constraint'
    }

    def explain_constraint_not_allowed():
        """
        When adding a column to an existing table, certain constraints can have
        unintentional side effects, like locking the table or introducing
        performance issues.

        For example, adding a ``DEFAULT`` constraint may hold a lock on the
        table while all existing rows are modified to fill in the default
        value.

        A ``UNIQUE`` constraint will require scanning the table to confirm
        there are no duplicates.

        On a particularly hot table, a ``FOREIGN`` constraint will introduce
        possibly dangerous overhead to confirm the referential integrity of
        each row.
        """

    def enable(self, ctx, config):
        disallowed = config.get('disallowed', [])
        if disallowed == []:
            raise RuleConfigurationException(
                    self, 'must specify `disallowed` constraints')

        constraints = set()

        for c in disallowed:
            ty = self._CONSTRAINT_MAP[c.upper()]
            if ty is None:
                raise RuleConfigurationException(
                        self, 'unknown constraint: `%s`' % c)

            constraints.add(ty)

        ctx.register('AlterTableCmd', self._check(constraints))

    @squabble.rule.node_visitor
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
