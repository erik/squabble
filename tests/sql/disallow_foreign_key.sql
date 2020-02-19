-- squabble-enable:DisallowForeignKey excluded=fk_allowed,new_table
-- >>> {"line": 7, "column": 47, "message_id": "DisallowedForeignKeyConstraint", "message_params": {"table": "foreign_key_reference"}}
-- >>> {"line": 8, "column": 53, "message_id": "DisallowedForeignKeyConstraint", "message_params": {"table": "inline_foreign_key_reference"}}
-- >>> {"line": 9, "column": 42, "message_id": "DisallowedForeignKeyConstraint", "message_params": {"table": "alter_table_with_fk_later"}}

-- Disallowed foreign keys
CREATE TABLE foreign_key_reference(foo_id int, FOREIGN KEY (foo_id) REFERENCES foo(pk));
CREATE TABLE inline_foreign_key_reference(foo_id int REFERENCES foo);
ALTER TABLE alter_table_with_fk_later ADD FOREIGN KEY (foo_id) REFERENCES foo(pk);

-- Allowed here
ALTER TABLE fk_allowed ADD COLUMN foo_id int REFERENCES foo(pk);
CREATE TABLE new_table(foo_id int REFERENCES foo(id));

-- No issue
ALTER TABLE alter_table_without_fk ADD COLUMN foo_id int;
ALTER TABLE alter_table_without_fk ADD UNIQUE (foo_id);
