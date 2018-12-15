-- enable:AddColumnDisallowConstraints disallowed=DEFAULT,FOREIGN
-- >>> 4 46 ERROR constraint_not_allowed

ALTER TABLE foobar ADD COLUMN colname coltype DEFAULT baz;

ALTER TABLE foobar ADD COLUMN colname coltype UNIQUE;
