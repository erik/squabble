Editor Integration
==================

Several editor syntax checkers already natively support the output
format for a similar tool, `sqlint <https://github.com/purcell/sqlint>`__,
which we can piggy-back off of by using the ``"sqlint"`` reporter.

Specific editors are mentioned below, but generally, if your editor
has support for ``sqlint`` and can customize the executable, try running
``squabble --reporter=sqlint`` instead!

emacs (via flycheck)
--------------------

The best way to configure squabble through flycheck would be to create
a new checker definition, which should Just Work when you open a SQL
file with flycheck turned on.

.. code-block:: elisp

  (flycheck-define-checker sql-squabble
    "A SQL syntax checker using the squabble tool.
  See URL `https://github.com/erik/squabble'."
    :command ("squabble" "--reporter=sqlint")
    :standard-input t
    :error-patterns
    ((warning line-start "stdin:" line ":" column ":WARNING "
              (message (one-or-more not-newline)
                       (zero-or-more "\n"))
              line-end)
     (error line-start "stdin:" line ":" column ":ERROR "
            (message (one-or-more not-newline)
                     (zero-or-more "\n"))
            line-end))
  :modes (sql-mode))

  (add-to-list 'flycheck-checkers 'sql-squabble)


Flycheck ships with support for `sqlint
<https://github.com/purcell/sqlint>`__, so if for whatever reason you
don't want to define a new checker, you should just be able to point
flycheck at the ``squabble`` executable.

.. code-block:: elisp

   (setq 'flycheck-sql-sqlint-executable "squabble")

Unfortunately flycheck does not allow user customization of the
command line arguments passed to the program, so you'll need to make
sure to have configuration file with ``{"reporter": "sqlint"}``.

vim (via syntastic)
-------------------

.. code-block:: vim

  let g:syntastic_sql_sqlint_exec = "squabble"
  let g:syntastic_sql_sqlint_args = "--reporter=sqlint"
