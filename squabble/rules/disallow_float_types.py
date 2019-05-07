import pglast

import squabble.rule
from squabble.lint import Severity
from squabble.message import Message
from squabble.rules import BaseRule
from squabble.util import format_type_name


def _parse_column_type(typ):
    """
    Feed column type name through pglast.

    >>> _parse_column_type('real')
    'pg_catalog.float4'

    >>> _parse_column_type('double precision')
    'pg_catalog.float8'
    """
    sql = 'CREATE TABLE _(_ {0});'.format(typ)

    create_table = pglast.Node(pglast.parse_sql(sql))[0].stmt
    type_name = create_table.tableElts[0].typeName

    return format_type_name(type_name)


class DisallowFloatTypes(BaseRule):
    """
    Prevent using approximate float point number data types.

    In SQL, the types ``FLOAT``, ``REAL``, and ``DOUBLE PRECISION`` are
    implemented as IEEE 754 floating point numbers, which will not be
    able to perfectly represent all numbers within their ranges.

    Often, they'll be "good enough", but when doing aggregates over a
    large table, or trying to store very large (or very small)
    numbers, errors can be exaggerated.

    Most of the time, you'll probably want to used a fixed-point
    number, such as ``NUMERIC(3, 4)``.

    Configuration ::

      { "DisallowFloatTypes": {} }
    """

    _INEXACT_TYPES = set(
        _parse_column_type(ty)
        for ty in ['real', 'float', 'double', 'double precision']
    )

    class LossyFloatType(Message):
        """
        The types ``FLOAT``, ``REAL``, and ``DOUBLE PRECISION`` are
        implemented as IEEE 754 floating point numbers, which by
        definition will not be able to perfectly represent all numbers
        within their ranges.

        This is an issue when performing aggregates over large numbers of
        rows, as errors can accumulate.

        Instead, using the fixed-precision numeric data types (``NUMERIC``,
        ``DECIMAL``) are likely the right choice for most cases.
        """
        TEMPLATE = 'tried to use a lossy float type instead of fixed precision'
        CODE = 1007

    def enable(self, root_ctx, _config):
        root_ctx.register('ColumnDef', self._check_column_def())

    @squabble.rule.node_visitor
    def _check_column_def(self, ctx, node):
        col_type = format_type_name(node.typeName)

        if col_type in self._INEXACT_TYPES:
            ctx.report(self.LossyFloatType(), node=node, severity=Severity.LOW)
