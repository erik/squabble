from pglast.enums import SQLValueFunctionOp

import squabble.rule
from squabble.lint import Severity
from squabble.message import Message
from squabble.rules import BaseRule
from squabble.util import format_type_name


class DisallowTimetzType(BaseRule):
    """
    Prevent using ``time with time zone``, along with ``CURRENT_TIME``.

    Postgres recommends never using this type, citing that it's only
    implemented for ANSI SQL compliance, and that ``timestamptz`` /
    ``timestamp with time zone`` is almost always a better solution.

    Configuration ::

       { "DisallowTimetzType": {} }
    """

    _DISALLOWED_TYPES = {
        'pg_catalog.timetz',
        'timetz',
    }

    class NoTimetzType(Message):
        """
        The type ``time with time zone`` is defined by the SQL standard, but
        the definition exhibits properties which lead to questionable
        usefulness.

        In most cases, a combination of ``date``, ``time``,
        ``timestamp without time zone``, and ``timestamp with time zone``
        should provide a complete range of date/time functionality required by
        any application.
        """

        TEMPLATE = 'use `timestamptz` instead of `timetz` in most cases'
        CODE = 1011

    class NoCurrentTime(Message):
        """
        ``CURRENT_TIME`` returns a ``time with time zone`` type, which is
        likely not what you want.

        In most cases, ``CURRENT_TIMESTAMP`` is the correct replacement.

        Some other options:

          - ``CURRENT_TIMESTAMP, now()`` - timestamp with time zone
          - ``LOCALTIMESTAMP`` - timestamp without time zone
          - ``CURRENT_DATE`` - date
          - ``LOCALTIME`` - time
        """

        TEMPLATE = 'use `CURRENT_TIMESTAMP` instead of `CURRENT_TIME`'
        CODE = 1012

    def enable(self, root_ctx, _config):
        root_ctx.register('ColumnDef', self._check_column_def())
        root_ctx.register('SQLValueFunction', self._check_function_call())

    @squabble.rule.node_visitor
    def _check_column_def(self, ctx, node):
        col_type = format_type_name(node.typeName)

        if col_type in self._DISALLOWED_TYPES:
            ctx.report(
                self.NoTimetzType(),
                node=node.typeName,
                severity=Severity.LOW)

    @squabble.rule.node_visitor
    def _check_function_call(self, ctx, node):
        if node.op == SQLValueFunctionOp.SVFOP_CURRENT_TIME:
            ctx.report(self.NoCurrentTime(), node=node, severity=Severity.LOW)
