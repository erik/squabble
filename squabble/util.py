"""
Odds and ends pieces that don't fit elsewhere, but aren't important
enough to have their own modules.
"""

import re


_RST_DIRECTIVE = re.compile(r'^\.\. [\w-]+:: \w+$\n', flags=re.MULTILINE)


def strip_rst_directives(string):
    """
    Strip reStructuredText directives out of a block of text.

    Lines containing a directive will be stripped out entirely

    >>> strip_rst_directives('hello\\n.. code-block:: foo\\nworld')
    'hello\\nworld'
    """

    return re.sub(_RST_DIRECTIVE, '', string)


def format_type_name(type_name):
    """
    Return a simple stringified version of a ``pglast.node.TypeName`` node.

    Note that this won't be suitable for printing, and ignores type
    modifiers (e.g. ``NUMERIC(3,4)`` => ``NUMERIC``).

    >>> import pglast
    >>> sql = 'CREATE TABLE _ (y time with time zone);'
    >>> node = pglast.Node(pglast.parse_sql(sql))
    >>> col_def = node[0]['stmt']['tableElts'][0]
    >>> format_type_name(col_def.typeName)
    'pg_catalog.timetz'
    """
    return '.'.join([p.string_value for p in type_name.names])
