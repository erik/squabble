import pglast

import squabble.rule
from squabble.lint import Severity
from squabble.message import Message
from squabble.rules import BaseRule
from squabble.util import format_type_name


class DisallowTimestampPrecision(BaseRule):
    """
    Prevent using ``TIMESTAMP(p)`` due to rounding behavior.

    For both ``TIMESTAMP(p)`` and ``TIMESTAMP WITH TIME ZONE(p)``, (as well as
    the corresponding ``TIME`` types) the optional precision parameter ``p``
    rounds the value instead of truncating.

    This means that it is possible to store values that are half a second in
    the future for ``p == 0``.

    To only enforce this rule for certain values of ``p``, set the
    configuration option ``allow_precision_greater_than``.

    Configuration ::

       { "DisallowTimetzType": {
           "allow_precision_greater_than": 0
         }
       }
    """

    _CHECKED_TYPES = {
        'pg_catalog.time',
        'pg_catalog.timetz',
        'pg_catalog.timestamp',
        'pg_catalog.timestamptz',
    }

    _DEFAULT_MIN_PRECISION = 9999

    class NoTimestampPrecision(Message):
        """
        Specifying a fixed precision for ``TIMESTAMP`` and ``TIME`` types will
        cause the database to round inserted values (instead of truncating, as
        one would expect).

        This rounding behavior means that some values that get inserted may be
        in the future, up to half a second with a precision of ``0``.

        Instead, explicitly using ``date_trunc('granularity', time)`` may be a
        better option.
        """
        TEMPLATE = "use `date_trunc` instead of fixed precision timestamps"
        CODE = 1014

    def enable(self, root_ctx, config):
        min_precision = int(
            config.get(
                'allow_precision_greater_than',
                self._DEFAULT_MIN_PRECISION))

        root_ctx.register('ColumnDef', self._check_column_def(min_precision))

    @squabble.rule.node_visitor
    def _check_column_def(self, ctx, node, min_precision):
        col_type = format_type_name(node.typeName)

        if col_type not in self._CHECKED_TYPES:
            return

        modifiers = node.typeName.typmods
        if modifiers == pglast.Missing or \
           len(modifiers) != 1 or \
           modifiers[0].val.node_tag != 'Integer':
            return

        if modifiers[0].val.ival.value <= min_precision:
            ctx.report(
                self.NoTimestampPrecision(),
                node=node.typeName,
                severity=Severity.LOW)
