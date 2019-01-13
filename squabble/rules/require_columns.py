import pglast
import pglast.printers

import squabble.rule
from squabble import RuleConfigurationException
from squabble.message import Message
from squabble.rules import BaseRule


def split_required_col(req):
    """
    Split columns as given as strings in the configuration.

    >>> split_required_col('col_a')
    ('col_a', None)
    >>> split_required_col('col_B,integer')
    ('col_b', 'integer')
    >>> split_required_col('col_c,some(parametric,type)')
    ('col_c', 'some(parametric,type)')
    """
    split = req.lower().split(',', 1)

    # no type, just a value
    if len(split) == 1:
        return (split[0], None)

    return (split[0], split[1])


def _normalize_columns(table_elts):
    """
    Return a list of (column name, column type) after pretty printing
    them using pglast.

    >>> import pglast.printer
    >>> create_table = pglast.parse_sql(
    ...   'CREATE TABLE _(COL1 foo.bar(baz,123), Col2 integer);')
    >>> table_elts = pglast.Node(create_table)[0].stmt.tableElts
    >>> _normalize_columns(table_elts)
    [('col1', 'foo.bar(baz, 123)'), ('col2', 'integer')]
    """
    # This is a pretty hacky implementation
    printer = pglast.printer.RawStream()
    columns = printer(table_elts).split(';')

    res = []

    for col in columns:
        name, typ = col.strip().split(' ', 1)
        res.append((name, typ))

    return res


def parse_column_type(typ):
    """
    Feed the column type through pglast to normalize naming

    e.g. `timestamp with time zone => timestamptz`.

    >>> parse_column_type('integer')
    'integer'
    >>> parse_column_type('custom(type)')
    'custom(type)'
    """
    sql = 'CREATE TABLE _(_ {0});'.format(typ)

    try:
        create_table = pglast.Node(pglast.parse_sql(sql))[0].stmt
        _, typ = _normalize_columns(create_table.tableElts)[0]
        return typ
    except pglast.parser.ParseError:
        raise RuleConfigurationException(
            RequireColumns, 'unable to parse column type "%s' % typ)


def get_required_columns(config):
    """
    Extracts the column name and normalizes types out of the config
    value for `RequireColumns`.

    >>> get_required_columns(['foo,int', 'Bar'])
    {'foo': 'integer', 'bar': None}
    """
    if not config:
        raise RuleConfigurationException(
            RequireColumns, 'must provide `required` columns')

    required = {}
    for req in config:
        column, type_str = split_required_col(req)
        typ = parse_column_type(type_str) if type_str else None

        required[column] = typ

    return required


class RequireColumns(BaseRule):
    """
    Require that newly created tables have specified columns.

    Configuration ::

        {
            "RequireColumns": {
                "required": ["column_foo,column_type", "column_bar"]
            }
        }

    If a column type is specified (like ``column_foo`` in the example
    configuration), the linter will make sure that the types match.

    Otherwise, only the presence of the column will be checked.
    """

    class MissingRequiredColumn(Message):
        CODE = 1005
        TEMPLATE = '"{tbl}" missing required column "{col}"'

    class ColumnWrongType(Message):
        CODE = 1006
        TEMPLATE = '"{tbl}.{col}" has type "{actual}" expected "{required}"'

    def enable(self, ctx, config):
        config = config.get('required', [])
        cols = get_required_columns(config)

        ctx.register('CreateStmt', self._check_create_table(cols))

    @squabble.rule.node_visitor
    def _check_create_table(self, ctx, node, required):
        table = node.relation
        columns = {}

        for col, typ in _normalize_columns(node.tableElts):
            columns[col] = {'type': typ, 'node': None}

        def _attach_column_node(_ctx, col):
            name = col.colname.value.lower()
            columns[name]['node'] = col

        ctx.register('ColumnDef', _attach_column_node)
        ctx.register_exit(
            lambda _ctx: self._check_required(_ctx, table, columns, required))

    def _check_required(self, ctx, table, columns, required):
        table_name = table.relname.value

        for col, typ in required.items():
            if col not in columns:
                ctx.report(
                    self.MissingRequiredColumn(tbl=table_name, col=col),
                    node=table)

                continue

            actual = columns[col]['type']
            if typ is not None and actual != typ:
                node = columns[col]['node']
                ctx.report(
                    self.ColumnWrongType(
                        tbl=table_name, col=col, required=typ, actual=actual),
                    node=node)
