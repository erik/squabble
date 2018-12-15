-- enable:DisallowChangeColumnType
-- >>> 4:46 ERROR change_type_not_allowed

ALTER TABLE foo ALTER COLUMN bar SET DATA TYPE baz;
