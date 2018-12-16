-- enable:DisallowChangeColumnType
-- >>> {"line": 4, "column": 47, "message_id": "change_type_not_allowed"}

ALTER TABLE foo ALTER COLUMN bar SET DATA TYPE baz;
