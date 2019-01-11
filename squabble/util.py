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
