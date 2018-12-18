import pglast

from squabble.rules import Rule


class DisallowRenameEnumValue(Rule):
    """
    Prevent renaming existing enum value.

    Configuration:

        "rules": {
            "DisallowChangeEnumValue": {}
        }

    Tags: backwards-compatibility
    """

    MESSAGES = {
        'rename_not_allowed': 'cannot rename existing enum value "{value}"'
    }

    def __init__(self, opts):
        self._opts = opts

    def enable(self, ctx):
        ctx.register('AlterEnumStmt', lambda c, n: self._check_enum(c, n))

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
