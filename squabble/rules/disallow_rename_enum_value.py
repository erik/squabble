import pglast

from squabble.rules import Rule


class DisallowRenameEnumValue(Rule):
    """
    Prevent renaming existing enum value.

    Configuration:

    .. code-block:: json

        { "DisallowChangeEnumValue": {} }

    Tags: backwards-compatibility
    """

    MESSAGES = {
        'rename_not_allowed': 'cannot rename existing enum value "{value}"'
    }

    def enable(self, ctx):
        ctx.register('AlterEnumStmt', self._check_enum())

    @Rule.node_visitor
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

        ctx.report(self, 'rename_not_allowed', params={'value': renamed})
