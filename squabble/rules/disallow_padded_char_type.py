import squabble.rule
from squabble.lint import Severity
from squabble.message import Message
from squabble.rules import BaseRule
from squabble.util import format_type_name


class DisallowPaddedCharType(BaseRule):
    """
    Prevent using ``CHAR(n)`` data type.

    Postgres recommends never using ``CHAR(n)``, as any value stored in this
    type will be padded with spaces to the declared width. This padding wastes
    space, but doesn't make operations on any faster; in fact the reverse,
    thanks to the need to strip spaces in many contexts.

    In most cases, the variable length types ``TEXT`` or ``VARCHAR`` will be
    more appropriate.

    Configuration ::

      { "DisallowPaddedCharType": {} }
    """

    _DISALLOWED_TYPES = {
        # note: ``bpchar`` for "bounded, padded char"
        'pg_catalog.bpchar'
    }

    class WastefulCharType(Message):
        """
        Any value stored in this type will be padded with spaces to the
        declared width. This padding wastes space, but doesn't make operations
        on any faster; in fact the reverse, thanks to the need to strip spaces
        in many contexts.

        From a storage point of view, ``CHAR(n)`` is not a fixed-width type.
        The actual number of bytes varies since characters (e.g. unicode) may
        take more than one byte, and the stored values are therefore treated as
        variable-length anyway (even though the space padding is included in
        the storage).

        If a maximum length must be enforced in the database, use
        ``VARCHAR(n)``, otherwise, consider using ``TEXT`` as a replacement.
        """
        TEMPLATE = '`CHAR(n)` has unnecessary space and time overhead,' + \
                   ' consider using `TEXT` or `VARCHAR`'
        CODE = 1013

    def enable(self, root_ctx, _config):
        root_ctx.register('ColumnDef', self._check_column_def())

    @squabble.rule.node_visitor
    def _check_column_def(self, ctx, node):
        col_type = format_type_name(node.typeName)

        if col_type in self._DISALLOWED_TYPES:
            ctx.report(
                self.WastefulCharType(),
                node=node,
                severity=Severity.LOW)
