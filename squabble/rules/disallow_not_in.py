from pglast.enums import A_Expr_Kind, BoolExprType, SubLinkType

import squabble.rule
from squabble.lint import Severity
from squabble.message import Message
from squabble.rules import BaseRule


class DisallowNotIn(BaseRule):
    """
    Prevent ``NOT IN`` as part of queries, due to the unexpected behavior
    around ``NULL`` values.

    Configuration: ::

        { "DisallowNotIn": {} }
    """

    class NotInNotAllowed(Message):
        """
        ``NOT IN`` (along with any expression containing ``NOT ... IN``) should
        generally not be used as it behaves in unexpected ways if there is a
        null present.

        .. code-block:: sql

            -- Always returns 0 rows
            SELECT * FROM foo WHERE col NOT IN (1, null);

            -- Returns 0 rows if any value of bar.x is null
            SELECT * FROM foo WHERE col NOT IN (SELECT x FROM bar);

        ``col IN (1, null)`` returns TRUE if ``col=1``, and NULL
        otherwise (i.e. it can never return FALSE).

        Since ``NOT (TRUE) = FALSE``, but ``NOT (NULL) = NULL``, it is not
        possible for this expression to return ``TRUE``.

        If you can guarantee that there will never be a null in the list of
        values, ``NOT IN`` is safe to use, but will not be optimized nicely.
        """
        CODE = 1010
        TEMPLATE = 'using `NOT IN` has nonintuitive behavior with null values'

    def enable(self, ctx, _config):
        ctx.register('A_Expr', self._check_not_in_list())

        def check_bool_expr(child_ctx, child_node):
            if child_node.boolop == BoolExprType.NOT_EXPR:
                child_ctx.register('SubLink', self._check_not_in_subquery())

        ctx.register('BoolExpr', check_bool_expr)

    @squabble.rule.node_visitor
    def _check_not_in_list(self, ctx, node):
        """Handles cases like ``WHERE NOT IN (1, 2, 3)``."""
        # We're only interested in `IN` expressions
        if node.kind != A_Expr_Kind.AEXPR_IN:
            return

        # Specifically only ``NOT IN``
        if node.name.string_value != "<>":
            return

        ctx.report(
            self.NotInNotAllowed(),
            node=node.rexpr[0],
            severity=Severity.LOW)

    @squabble.rule.node_visitor
    def _check_not_in_subquery(self, ctx, node):
        """Handles cases like ``WHERE NOT IN (SELECT * FROM foo)``."""

        if node.subLinkType != SubLinkType.ANY_SUBLINK:
            return

        ctx.report(
            self.NotInNotAllowed(),
            node=node,
            severity=Severity.LOW)
