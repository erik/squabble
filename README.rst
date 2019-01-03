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

Squabble works to help automate the process of reviewing SQL migrations
by catching simple mistakes, such as:

-  Changing the type of an existing column
-  Adding a new column with a default value or ``NOT NULL`` constraint
-  Building an index without using ``CONCURRENTLY``

For more information on why these particular cases can be dangerous:

-  https://www.braintreepayments.com/blog/safe-operations-for-high-volume-postgresql/
-  https://blog.codeship.com/rails-migrations-zero-downtime/
-  https://stripe.com/blog/online-migrations

Currently, most of the rules have been focused on Postgres and its
quirks. However, squabble can parse any ANSI SQL and new rules that are
specific to other databases are appreciated!

Installation
------------

.. code:: console

   $ pip3 install squabble
   $ squabble --help

.. note::

   Squabble is only supported on Python 3.5+

If you’d like to install from source:

.. code:: console

   $ git clone https://github.com/erik/squabble.git && cd squabble
   $ python3 -m venv ve && source ve/bin/activate
   $ python setup.py install
   $ squabble --help

Configuration
-------------

To see a list of rules, try

.. code:: console

   $ squabble --list-rules

Then, to show more verbose information about a rule (such as rationale
and configuration options)

.. code:: console

   $ squabble --show-rule AddColumnsDisallowConstraints

Once a configuration file is in place, it can be passed explicitly on
the command line, or automatically looked up.

.. code:: console

   $ squabble -c path/to/config ...

If not explicitly given on the command line, squabble will look for a
file named ``.squabblerc`` in the following places (in order):

-  ``./.squabblerc``
-  ``(git_repo_root)/.squabblerc``
-  ``~/.squabblerc``

Example Configuration
~~~~~~~~~~~~~~~~~~~~~

.. code:: json

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


Acknowledgments
---------------

This project would not be possible without:

-  `libpg_query <https://github.com/lfittl/libpg_query>`__ - Postgres
   query parser
-  `pglast <https://github.com/lelit/pglast>`__ - Python bindings to
   libpg_query
-  Postgres - …obviously

.. |build-status| image:: https://img.shields.io/travis/erik/squabble.svg?style=flat
    :alt: build status
    :target: https://travis-ci.org/erik/squabble

.. |docs| image:: https://readthedocs.org/projects/squabble/badge/?version=latest
    :alt: Documentation Status
    :target: https://squabble.readthedocs.io/en/latest/?badge=latest

.. |pypi| image:: https://img.shields.io/pypi/v/squabble.svg
   :alt: PyPI version
   :target: https://pypi.org/project/squabble
