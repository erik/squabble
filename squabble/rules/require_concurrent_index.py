import pglast

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

    Tags: performance
    """
    MESSAGES = {
        'index_not_concurrent': 'index "{name}" not created `CONCURRENTLY`'
    }

    def enable(self, ctx):
        include_new = self._options.get('include_new_tables', False)
        tables = set()

        # Keep track of CREATE TABLE statements if we're not including
        # them in our check.
        if not include_new:
            ctx.register('CreateStmt', self._create_table(tables))

        ctx.register('IndexStmt', self._create_index(tables))

    @Rule.node_visitor
    def _create_table(self, ctx, node, tables):
        table = node.relation.relname.value.lower()
        logger.debug('found a new table: %s', table)

        tables.add(table)

    @Rule.node_visitor
    def _create_index(self, ctx, node, tables):
        index_name = 'unnamed'
        if node.idxname != pglast.Missing:
            index_name = node.idxname.value

        concurrent = node.concurrent

        # Index was created concurrently, nothing to do here
        if concurrent != pglast.Missing and concurrent.value is True:
            return

        table = node.relation.relname.value.lower()

        # This is a new table, don't alert on it
        if table in tables:
            return

        ctx.report(
            self,
            'index_not_concurrent',
            params={'name': index_name},
            node=node.relation)
