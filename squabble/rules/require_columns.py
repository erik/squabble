import pglast
import pglast.printers

from squabble import RuleConfigurationException
from squabble.rules import Rule


def split_required_col(req):
    """
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
    # >>> import pglast.printer
    # >>> create_table = pglast.parse_sql('CREATE TABLE _(col1 foo.bar(baz,123), col2 integer);')
    # >>> table_elts = pglast.Node(create_table)[0].stmt.tableElts
    # >>> _normalize_columns(table_elts)
    # [('col1', 'foo.bar(baz, 123)'), ('col2', 'integer')]
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
    Feed the column type through pglast to normalize naming.
    e.g. `timestamp with time zone => timestamptz`

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


class RequireColumns(Rule):
    """
    Require that newly created tables have specified columns.

    Configuration:

        "rules": {
            "RequireColumns": {
                "required": ["column_foo,column_type", "column_bar"]
            }
        }

    If a column type is specified (like `column_foo` in the example
    configuration), the linter will make sure that the types match.

    Otherwise, only the presence of the column will be checked.

    """

    MESSAGES = {
        'missing_required_column': '"{tbl}" missing required column "{col}"',
        'column_wrong_type': '"{tbl}.{col}" has type "{actual}" expected "{required}"'
    }

    def __init__(self, opts):
        required = opts.get('required', [])

        if not required:
            raise RuleConfigurationException(
                self, 'must provide `required` columns')

        self._required = {}
        for req in required:
            column, type_str = split_required_col(req)
            typ = parse_column_type(type_str) if type_str else None

            self._required[column] = typ

    def enable(self, ctx):
        ctx.register('CreateStmt', lambda c, n: self._check_create_table(c, n))

    def _check_create_table(self, ctx, node):
        # TODO: We can do better location reporting here...
        table_node = node.relation
        table_name = table_node.relname.value
        seen_columns = {}

        for col, typ in _normalize_columns(node.tableElts):
            seen_columns[col] = typ

        for col, typ in self._required.items():
            if col not in seen_columns:
                ctx.report(
                    self,
                    'missing_required_column',
                    params={'tbl': table_name, 'col': col},
                    node=table_node)
                continue

            actual = seen_columns[col]
            if typ is not None and actual != typ:
                ctx.report(
                    self,
                    'column_wrong_type',
                    params={'tbl': table_name, 'col': col, 'required': typ, 'actual': actual},
                    node=table_node)
