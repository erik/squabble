-- enable:AddColumnDisallowConstraints disallowed=DEFAULT,FOREIGN,UNIQUE

ALTER TABLE foobar ADD COLUMN colname coltype DEFAULT baz;

ALTER TABLE foobar ADD COLUMN colname coltype UNIQUE;
