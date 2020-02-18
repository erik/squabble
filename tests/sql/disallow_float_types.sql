-- squabble-enable:DisallowFloatTypes
-- >>> {"line": 8,  "column": 2, "message_id": "LossyFloatType"}
-- >>> {"line": 9,  "column": 2, "message_id": "LossyFloatType"}
-- >>> {"line": 15, "column": 2, "message_id": "LossyFloatType"}

CREATE TABLE foo (
  -- should not pass
  bar  REAL,
  baz  DOUBLE PRECISION,
  -- should pass
  quux INT
);

ALTER TABLE foo ADD COLUMN
  bar FLOAT;
