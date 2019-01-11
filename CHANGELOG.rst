Changelog
=========

v1.1.0-dev (unreleased)
-----------------------

New
~~~

- Add ``RequireForeignKey`` rule.

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
- Fix calls to logger to correctly report module.

v1.0.0 (2019-01-05)
-------------------

New
~~~
- Added -e, --explain to print out detailed explanation of why a
  message was raised.
- Added -r, --reporter to override reporter on command line.
- Added support for reading from stdin.
- Added ``full`` preset.
- Added ``Severity`` enum for LintIssues.
- Added ``sqlint`` reporter for compatibility with tooling targeting
  sqlint.
- Added ``DisallowFloatTypes`` rule.
- Added user facing documentation for https://squabble.readthedocs.org

Changes
~~~~~~~
- Improved existing API documentation with type signatures and examples.
- Removed BaseRule.MESSAGES in favor of squabble.message.Message

v0.1.0 (2018-12-27)
-------------------

- Initial release.