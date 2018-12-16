import pglast
from pglast.enums import AlterTableType, ConstrType

from squabble import logger

from squabble.rules import Rule


class RequireConcurrentIndex(Rule):
    """
    Require all new indexes to be created with `CONCURRENTLY` so they won't
    block.

    By default, tables created in the same index are exempted, since they are
    known to be empty. This can be changed with the option
    `"include_new_tables": true`

    Configuration:

        "rules": {
            "RequireConcurrentIndex": {
                "include_new_tables": false
            }
        }
    """

    MESSAGES = {
        'index_not_concurrent': 'index "{name}" not created with `CONCURRENTLY`'
    }

    def __init__(self, opts):
        self._include_new = opts.get('include_new_tables', False)
        self._tables = set()

    def enable(self, ctx):
        # Keep track of CREATE TABLE statements if we're not including
        # them in our check.
        if not self._include_new:
            ctx.register('CreateStmt', lambda c, n: self._create_table(c, n))

        ctx.register('IndexStmt', lambda c, n: self._create_index(c, n))

    def _create_table(self, ctx, node):
        table = node.relation.relname.value.lower()
        logger.debug('found a new table: %s', table)
        self._tables.add(table)

    def _create_index(self, ctx, node):
        index_name = 'unnamed'
        if node.idxname != pglast.Missing:
            index_name = node.idxname.value

        concurrent = node.concurrent

        # Index was created concurrently, nothing to do here
        if concurrent != pglast.Missing and concurrent.value is True:
            return

        table = node.relation.relname.value.lower()

        # This is a new table, don't alert on it
        if table in self._tables:
            return

        ctx.report(
            self,
            'index_not_concurrent',
            params={'name': index_name},
            node=node.relation)
