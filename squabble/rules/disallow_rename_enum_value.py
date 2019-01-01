import pglast

import squabble.rule
from squabble.message import Message
from squabble.rules import BaseRule


class DisallowRenameEnumValue(BaseRule):
    """
    Prevent renaming existing enum value.

    Configuration:

    .. code-block:: json

        { "DisallowChangeEnumValue": {} }
    """

    class RenameNotAllowed(Message):
        """
        Renaming an existing enum value may be backwards compatible
        with code that is live in production.
        """
        TEMPLATE = 'cannot rename existing enum value "{value}"'

    def enable(self, ctx, _config):
        ctx.register('AlterEnumStmt', self._check_enum())

    @squabble.rule.node_visitor
    def _check_enum(self, ctx, node):
        """
        Node is an 'AlterEnumStmt' value

        {
            'AlterEnumStmt': {
                'newVal': 'bar',
                'oldVal': 'foo',   # present if we're renaming
            }
        }
        """

        # Nothing to do if this isn't a rename
        if node.oldVal == pglast.Missing:
            return

        renamed = node.oldVal.value

        ctx.report(self.RenameNotAllowed(value=renamed))
