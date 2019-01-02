Writing Plugins
===============

Squabble supports loading rule definitions from directories specified in the
``.squabblerc`` configuration file.

Every Python file in the list of directories will be loaded and any classes
that inherit from :class:`squabble.rules.BaseRule` will be registered and
available for use.


Configuration
-------------

::

   {
     "plugins": [
       "/path/to/plugins/",
       ...
     ]
   }

Concepts
--------

Rules
~~~~~

Rules are classes which inherit from :class:`squabble.rules.BaseRule` and
are responsible for checking the abstract syntax tree of a SQL file.

At a minimum, each rule will define ``def enable(self, root_context, config)``,
which is responsible for doing any initialization when the rule is enabled.

Rules register callback functions to trigger when certain nodes of the abstract
syntax tree are hit. Rules will report messages_ to indicate any issues
discovered.

For example ::

  class MyRule(squabble.rules.BaseRule):
      def enable(self, context, config):
          ...

Could be configured with this ``.squabblerc`` ::

  {"rules": {"MyRule": {"foo": "bar"}}}

``enable()`` would be passed ``config={"foo": "bar"}``.

.. _messages:

Messages
~~~~~~~~

Messages inherit from :class:`squabble.message.Message`, and are used to define
specific kinds of lint exceptions a rule can uncover.

At a bare minimum, each message class needs a ``TEMPLATE`` class variable,
which is used when formatting the message to be printed on the command line.

For example ::

  class BadlyNamedColumn(squabble.message.Message):
      """
      Here are some more details about ``BadlyNamedColumn``.

      This is where you would explain why this message is relevant,
      how to resolve it, etc.
      """

      TEMPLATE = 'tried to {foo} when you should have done {bar}!'

  >>> msg = MyMessage(foo='abc', bar='xyz')
  >>> msg.format()
  'tried to abc when you should have done xyz'
  >>> msg.explain()
  'Here are some more details ...

Messages may also define a ``CODE`` class variable, which is an integer which
uniquely identifies the class. If not explicitly specified, one will be
assigned, starting at ``9000``. These can be used by the ``--explain`` command
line flag ::

  $ squabble --explain 9001
  BadlyNamedColumn
      Here are some more details about ``BadlyNamedColumn``.

      ...

Lint context
~~~~~~~~~~~~

Each instance of :class:`squabble.lint.LintContext` holds the callback
functions that have been registered at or below a particular node in the
abstract syntax tree, as well as being responsible for reporting any messages
that get raised.

When the ``enable()`` function for a class inheriting from
:class:`squabble.rules.BaseRule` is called, it will be passed a context
pointing to the root node of the syntax tree. Every callback function will be
passed a context scoped to the node that triggered the callback.

::

   def enable(root_context, _config):
       root_context.register('CreateStmt', create_table_callback)

   def create_table_callback(child_context, node):
       # register a callback that is only scoped to this ``node``
       child_context.register('ColumnDef', column_def_callback):

   def column_def_callback(child_context, node):
       ...

Details
-------

-  Parsing is done using
   `libpg_query <https://github.com/lfittl/libpg_query>`__, a Postgres
   query parser.

   -  *theoretically* it will work with other SQL dialects

-  Rules are implemented by registering callbacks while traversing the
   Abstract Syntax Tree of the query.

   -  e.g. entering a ``CREATE TABLE`` node registers a callback for a
      column definition node, which checks that the column type is
      correct.

As a somewhat unfortunate consequence of our reliance on libpg_query,
the abstract syntax tree is very, very specific to Postgres. While
developing new rules, it will be necessary to reference the `Postgres
AST
Node <https://git.postgresql.org/gitweb/?p=postgresql.git;a=blob;f=src/include/nodes/parsenodes.h;hb=HEAD>`__
source listing, or, more readably, the `Python
bindings <https://github.com/lelit/pglast/tree/master/pglast/enums>`__.

Example Rule
------------

.. code-block:: python

   import squabble.rule
   from squabble.message import Message
   from squabble.rules import BaseRule

   class AllTablesMustBeLoud(BaseRule):
       """
       A custom rule which makes sure that all table names are
       in CAPSLOCK NOTATION.
       """

       class TableNotLoudEnough(Message):
           """Add more details about the message here"""
           CODE = 9876
           TEMPLATE = 'table "{name}" not LOUD ENOUGH'

       def enable(self, root_ctx, config):
           """
           Called before the root AST node is traversed. Here's where
           most callbacks should be registered for different AST
           nodes.

           Each linter is initialized once per file that it is being
           run against. `config` will contain the merged base
           configuration with the file-specific configuration options
           for this linter.
           """

           # Register that any time we see a `CreateStmt`
           # (`CREATE TABLE`), call self._check()
           root_ctx.register('CreateStmt', self._check_create())

           # When we exit the root `ctx`, call `self._on_finish()`
           root_ctx.register_exit(lambda ctx: self._on_finish(ctx))

       # node_visitor will pass in `ctx, node` for you so there's no
       # need to use a lambda
       @squabble.rule.node_visitor
       def _check(self, ctx, node):
           """
           Called when we enter a 'CreateStmt' node. Here we can
           register more callbacks if we need to, or do some checking
           based on the `node` which will be the AST representation of
           a `CREATE TABLE`.
           """

           table_name = node.relation.relname.value
           if table_name != table_name.upper():
               # Report an error if this table was not SCREAMING_CASE
               ctx.report(
                   self.TableNotLoudEnough(name=table_name),
                   node=node.relation)
