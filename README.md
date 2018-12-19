# squabble

Catch unsafe SQL migrations.

```sql
-- sql/migration.sql:4:46 ERROR: column "uh_oh" has a disallowed constraint
ALTER TABLE big_table ADD COLUMN uh_oh integer DEFAULT 0;
                                               ^
```

Squabble works to help automate the process of reviewing SQL migrations by
catching simple mistakes, such as:

  - Changing the type of an existing column
  - Adding a new column with a default value or `NOT NULL` constraint
  - Building an index without using `CONCURRENTLY`

Currently, most of the rules have been focused on Postgres and its
quirks. However, squabble can parse any ANSI SQL and new rules that are
specific to other databases are appreciated!

## Installation

Not on PyPI yet, so for now, have to go from source.

``` console
$ git clone https://github.com/erik/squabble.git && cd squabble
$ python3 -m venv ve && source ve/bin/activate
$ python setup.py install
$ squabble --help
```

## Configuration

To see a list of rules, try

``` console
$ squabble --list-rules
```

Then, to show more verbose information about a rule (such as rationale and
configuration options)

``` console
$ squabble --show-rule AddColumnsDisallowConstraints
```

``` console
$ squabble -c path/to/config ...
```

If not explicitly given on the command line, squabble will look for a file
named `.squabblerc` in the following places (in order):

 - `./.squabblerc`
 - `(git_repo_root)/.squabblerc`
 - `~/.squabblerc`

### Example Configuration

``` json
{
  "reporter": "color|plain",

  "plugins": [
    "/some/directory/with/custom/rules"
  ],

  "rules": {
    "AddColumnsDisallowConstraints": {
      "disallowed": ["DEFAULT", "FOREIGN", "NOT NULL"]
    }
  }
}
```

## nitty gritty

- Parsing is done using [libpg_query](https://github.com/lfittl/libpg_query), a
  Postgres query parser.
  - _theoretically_ it will work with other SQL dialects

- Rules are implemented by registering callbacks while traversing the Abstract
  Syntax Tree of the query.
  - e.g. entering a `CREATE TABLE` node registers a callback for a column
    definition node, which checks that the column type is correct.


## Writing your own lint rules

As a somewhat unfortunate consequence of our reliance on libpg_query,
the abstract syntax tree is very, very specific to Postgres. While developing
new rules, it will be necessary to reference the
[Postgres AST Node](https://git.postgresql.org/gitweb/?p=postgresql.git;a=blob;f=src/include/nodes/parsenodes.h;hb=HEAD)
source listing, or, more readably, the
[Python bindings](https://github.com/lelit/pglast/tree/master/pglast/enums).

``` python
from squabble import rule

class AllTablesMustBeLoud(Rule):
    """
    A custom rule which makes sure that all table names are expressed
    in CAPSLOCK NOTATION.
    """

    # Define the different message types that this Rule can return
    MESSAGES = {
        'table_not_loud_enough': 'table "{name}" not LOUD ENOUGH'
    }

    def __init__(self, options):
        """
        Each linter is initialized once per file that it is being run
        against. `options` will contain the merged base configuration
        with the file-specific configuration options for this linter.
        """
        pass

    def enable(self, root_ctx):
        """
        Called before the root AST node is traversed. Here's where most
        callbacks should be registered for different AST nodes.
        """

        # Register that any time we see a `CreateStmt` (`CREATE TABLE`), call
        # self._check()
        root_ctx.register('CreateStmt', lambda ctx, node: self._check(ctx, node))

        # When we exit the root `ctx`, call `self._on_finish()`
        root_ctx.register_exit(lambda ctx: self._on_finish(ctx))

    def _check(self, ctx, node):
        """
        Called when we enter a 'CreateStmt' node. Here we can register more
        callbacks if we need to, or do some checking based on the `node` which
        will be the AST representation of a `CREATE TABLE`.
        """

        table_name = node.relation.relname.value
        if table_name != table_name.upper():
            # Report an error if this table was not SCREAMING_CASE
            ctx.report(
                self,
                'table_name_not_loud_enough',
                params={'name': table_name},
                node=node.relation)

```

## Acknowledgments

This project would not be possible without:

- [libpg_query](https://github.com/lfittl/libpg_query) - Postgres query parser
- [pglast](https://github.com/lelit/pglast) - Python bindings to libpg_query
- Postgres - ...obviously
