-- enable:AddColumnDisallowConstraints disallowed=DEFAULT,FOREIGN
-- >>> {"line": 4, "column": 46, "message_id": "constraint_not_allowed"}

ALTER TABLE foobar ADD COLUMN colname coltype DEFAULT baz;

ALTER TABLE foobar ADD COLUMN colname coltype UNIQUE;
