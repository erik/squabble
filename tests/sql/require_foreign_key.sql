-- enable:RequireForeignKey
-- >>> {"line": 12, "column": 24, "message_id": "MissingForeignKeyConstraint"}
-- >>> {"line": 19, "column": 46, "message_id": "MissingForeignKeyConstraint"}


CREATE TABLE doesnt_match_column_regex(foo_id_not_a_references int);

CREATE TABLE inline_fk(foo_id int REFERENCES foo(id));

CREATE TABLE inline_fk(foo_id int, FOREIGN KEY (foo_id) REFERENCES foo(pk));

CREATE TABLE missing_fk(foo_id int);

ALTER TABLE alter_table_with_fk ADD COLUMN foo_id int REFERENCES foo(pk);

ALTER TABLE alter_table_with_fk_later ADD COLUMN foo_id int;
ALTER TABLE alter_table_with_fk_later ADD FOREIGN KEY (foo_id) REFERENCES foo(pk);

ALTER TABLE alter_table_without_fk ADD COLUMN foo_id int;
ALTER TABLE alter_table_without_fk ADD UNIQUE (foo_id);
