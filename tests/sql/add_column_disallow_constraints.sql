-- enable:AddColumnDisallowConstraints disallowed=DEFAULT,FOREIGN
-- >>> {"line": 4, "column": 46, "message_id": "ConstraintNotAllowed"}

ALTER TABLE foobar ADD COLUMN colname coltype DEFAULT baz;

ALTER TABLE foobar ADD COLUMN colname coltype UNIQUE;

ALTER TABLE foobar ADD COLUMN colname coltype;

ALTER TABLE foobar ADD CONSTRAINT new_constraint UNIQUE (foo);
