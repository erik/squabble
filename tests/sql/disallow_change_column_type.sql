-- squabble-enable:DisallowChangeColumnType
-- >>> {"line": 4, "column": 47, "message_id": "ChangeTypeNotAllowed"}

ALTER TABLE foo ALTER COLUMN bar SET DATA TYPE baz;

ALTER TABLE foo ALTER COLUMN bar DROP DEFAULT;
