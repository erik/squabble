import logging

import pglast

import squabble.rule
from squabble.message import Message
from squabble.rules import BaseRule


logger = logging.getLogger(__name__)


class RequireConcurrentIndex(BaseRule):
    """
    Require all new indexes to be created with ``CONCURRENTLY`` so they won't
    block.

    By default, tables created in the same file as the index are exempted,
    since they are known to be empty. This can be changed with the option
    ``"include_new_tables": true``.

    Configuration: ::

        {
            "RequireConcurrentIndex": {
                "include_new_tables": false
            }
        }
    """

    class IndexNotConcurrent(Message):
        """
        Adding a new index to an existing table may hold a full table lock
        while the index is being built. On large tables, this may take a long
        time, so the preferred approach is to create the index concurrently
        instead.

        .. code-block:: sql

           -- Don't do this
           CREATE INDEX users_by_name ON users(name);

           -- Try this instead
           CREATE INDEX CONCURRENTLY users_by_name ON users(name);
        """
        CODE = 1001
        TEMPLATE = 'index "{name}" not created `CONCURRENTLY`'

    def enable(self, ctx, config):
        include_new = config.get('include_new_tables', False)
        tables = set()

        # Keep track of CREATE TABLE statements if we're not including
        # them in our check.
        if not include_new:
            ctx.register('CreateStmt', self._create_table(tables))

        ctx.register('IndexStmt', self._create_index(tables))

    @squabble.rule.node_visitor
    def _create_table(self, ctx, node, tables):
        table = node.relation.relname.value.lower()
        logger.debug('found a new table: %s', table)

        tables.add(table)

    @squabble.rule.node_visitor
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
            self.IndexNotConcurrent(name=index_name),
            node=node.relation)
