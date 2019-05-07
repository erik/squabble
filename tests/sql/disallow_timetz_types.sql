-- enable:DisallowTimetzType
-- >>> {"line": 15, "column": 6, "message_id": "NoTimetzType"}
-- >>> {"line": 16, "column": 6, "message_id": "NoTimetzType"}
-- >>> {"line": 24, "column": 2, "message_id": "NoCurrentTime"}


CREATE TABLE foo (
  good timestamp,
  good timestamp without time zone,
  good timestamptz,
  good timestamp with time zone,
  good time,
  good time without time zone,

  bad timetz,
  bad time with time zone
);

SELECT
  CURRENT_TIMESTAMP as good,
  LOCALTIMESTAMP as good,
  CURRENT_DATE as good,
  now() as good,
  CURRENT_TIME as bad
FROM xyz;
