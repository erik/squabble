squabble
========

|build-status| |docs| |pypi|

Catch unsafe SQL migrations.

.. code:: console

  $ squabble sql/migration.sql
  sql/migration.sql:4:46 ERROR: column "uh_oh" has a disallowed constraint [1004]
  ALTER TABLE big_table ADD COLUMN uh_oh integer DEFAULT 0;
                                                 ^
  # Use --explain to get more information on a lint violation
  $ squabble --explain 1004
  ConstraintNotAllowed
       When adding a column to an existing table, certain constraints can have
       unintentional side effects, like locking the table or introducing
       performance issues.
       ...

Squabble can also be `integrated with your editor
<https://squabble.rtfd.io/en/latest/editors.html>`__ to catch errors in
SQL files.

.. code:: console

  $ echo 'SELECT * FROM WHERE x = y;' | squabble --reporter=plain
  stdin:1:15 CRITICAL: syntax error at or near "WHERE"

Currently, most of the rules have been focused on Postgres and its
quirks. However, squabble can parse any ANSI SQL and new rules that are
specific to other databases are appreciated!

Installation
------------

.. code-block:: console

   $ pip3 install squabble
   $ squabble --help

.. note::

   Squabble is only supported on Python 3.5+

If you’d like to install from source:

.. code-block:: console

   $ git clone https://github.com/erik/squabble.git && cd squabble
   $ python3 -m venv ve && source ve/bin/activate
   $ python setup.py install
   $ squabble --help

Configuration
-------------

To see a list of rules, try

.. code-block:: console

   $ squabble --list-rules

Then, to show more verbose information about a rule (such as rationale
and configuration options)

.. code-block:: console

   $ squabble --show-rule AddColumnsDisallowConstraints

Once a configuration file is in place, it can be passed explicitly on
the command line, or automatically looked up.

.. code-block:: console

   $ squabble -c path/to/config ...

If not explicitly given on the command line, squabble will look for a
file named ``.squabblerc`` in the following places (in order):

-  ``./.squabblerc``
-  ``(git_repo_root)/.squabblerc``
-  ``~/.squabblerc``

Per-File Configuration
~~~~~~~~~~~~~~~~~~~~~~

Configuration can also be applied at the file level by using SQL line comments
in the form ``-- enable:RuleName`` or ``-- disable:RuleName``.

For example, to disable ``RuleA`` and enable ``RuleB`` just for one file,
this could be done:

.. code-block:: sql

   -- disable:RuleA
   -- enable:RuleB config=value array=1,2,3
   SELECT email FROM users WHERE ...;


Example Configuration
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: json

   {
     "reporter": "color",

     "plugins": [
       "/some/directory/with/custom/rules"
     ],

     "rules": {
       "AddColumnsDisallowConstraints": {
         "disallowed": ["DEFAULT", "FOREIGN", "NOT NULL"]
       }
     }
   }

Prior Art
---------

``squabble`` is of course not the first tool in this space. If it
doesn't fit your needs, consider one of these tools:

- `sqlcheck <https://github.com/jarulraj/sqlcheck>`__ - regular
  expression based (rather than parsing), focuses more on ``SELECT``
  statements than migrations.
- `sqlint <https://github.com/purcell/sqlint>`__ - checks that the
  syntax of a file is valid. Uses the same parsing library as
  squabble.
- `sqlfluff <https://github.com/alanmcruickshank/sqlfluff>`__ -
  focused more on style and formatting, seems to still be a work in
  progress.


Acknowledgments
---------------

This project would not be possible without:

-  `libpg_query <https://github.com/lfittl/libpg_query>`__ - Postgres
   query parser
-  `pglast <https://github.com/lelit/pglast>`__ - Python bindings to
   libpg_query
-  Postgres - …obviously

The `logo image <https://thenounproject.com/term/argue/148100/>`__ used
in the documentation is created by Gianni - Dolce Merda from the Noun
Project.

.. |build-status| image:: https://img.shields.io/travis/erik/squabble.svg?style=flat
    :alt: build status
    :target: https://travis-ci.org/erik/squabble

.. |docs| image:: https://readthedocs.org/projects/squabble/badge/?version=latest
    :alt: Documentation Status
    :target: https://squabble.readthedocs.io/en/latest/?badge=latest

.. |pypi| image:: https://img.shields.io/pypi/v/squabble.svg
   :alt: PyPI version
   :target: https://pypi.org/project/squabble
