Changelog
=========

v1.4.0 (2020-02-18)
-------------------

New
~~~

- Added `precommit <https://pre-commit.com/>`__ hook definition (Thanks
  @PhilipTrauner!)
- Added ``squabble-disable`` configuration to disable all lint checks for a
  file.

Changes
~~~~~~~

- Per-file configuration is now done using ``squabble-enable:rule`` and
  ``squabble-disable:rule``. The original ``enable:rule`` format will continue
  to be supported, but is deprecated.


v1.3.3 (2019-08-27)
-------------------

Fixes
~~~~~

- Fix crash when handling SQL files containing only comments.

v1.3.2 (2019-07-30)
-------------------

Fixes
~~~~~

- Prevent crash when running ``RequireForeignKey`` rule against a
  ``CREATE TABLE`` statement with no columns defined.
- Fix Emacs Flycheck integration documentation.

v1.3.1 (2019-05-15)
-------------------

Changes
~~~~~~~

- Upgrade ``pglast`` to version ``1.4``.

Fixes
~~~~~

- Fixed standard input reader to not print a stack trace on interrupt.


v1.3.0 (2019-05-10)
-------------------

New
~~~

- Added ``-x, --expanded`` to show explanations of message codes after linting.
- Added ``DisallowNotIn`` rule.
- Added ``DisallowPaddedCharType`` rule.
- Added ``DisallowTimetzType`` rule.
- Added ``DisallowTimestampPrecision`` rule.

Changes
~~~~~~~

- Modified ``-p, --preset`` to allow multiple presets to be used at once.
- Update packaging to run tests through ``python setup.py test``.

Fixes
~~~~~

- Small documentation fixes for rules.

v1.2.0 (2019-01-14)
-------------------

New
~~~

- Added ``DisallowForeignKey`` rule.

Changes
~~~~~~~

- Allow rule descriptions to span multiple lines.
- Add ``DisallowForeignKey``, ``RequireForeignKey`` to ``"full"`` preset.

Fixes
~~~~~

- Fix ``RequireColumns`` to work with irregular casing.

v1.1.0 (2019-01-11)
-------------------

New
~~~

- Added ``RequireForeignKey`` rule.

Changes
~~~~~~~

- Split ``"postgres"`` preset into ``"postgres"`` and
  ``"postgres-zero-downtime"``.
- Strip RST code directives from message explanations and rules.
- Sort API documentation based on file order rather than
  alphabetically.

Fixes
~~~~~

- Support DOS ``\r\n`` line-endings for reporting issue location.
- Fixed calls to logger to correctly report module.

v1.0.0 (2019-01-05)
-------------------

New
~~~
- Added ``-e, --explain`` to print out detailed explanation of why a
  message was raised.
- Added ``-r, --reporter`` to override reporter on command line.
- Added support for reading from stdin.
- Added ``full`` preset.
- Added ``Severity`` enum for LintIssues.
- Added ``sqlint`` reporter for compatibility with tooling targeting
  sqlint.
- Added ``DisallowFloatTypes`` rule.
- Added user facing documentation for https://squabble.readthedocs.org

Changes
~~~~~~~
- Improved existing API documentation with type signatures and
  examples.
- Removed ``BaseRule.MESSAGES`` in favor of
  ``squabble.message.Message``.

v0.1.0 (2018-12-27)
-------------------

- Initial release.
