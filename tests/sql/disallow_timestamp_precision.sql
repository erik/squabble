-- squabble-enable:DisallowTimestampPrecision allow_precision_greater_than=5
-- >>> {"line": 24, "column": 6, "message_id": "NoTimestampPrecision"}
-- >>> {"line": 25, "column": 6, "message_id": "NoTimestampPrecision"}
-- >>> {"line": 26, "column": 6, "message_id": "NoTimestampPrecision"}
-- >>> {"line": 28, "column": 6, "message_id": "NoTimestampPrecision"}
-- >>> {"line": 29, "column": 6, "message_id": "NoTimestampPrecision"}
-- >>> {"line": 30, "column": 6, "message_id": "NoTimestampPrecision"}

CREATE TABLE foo (
  good timestamp,
  good timestamp with time zone,

  good timestamp(10),
  good timestamp(10) with time zone,
  good timestamp(10) without time zone,

  good time,
  good time with time zone,

  good time(10),
  good time(10) with time zone,
  good time(10) without time zone,

  bad timestamp(0),
  bad timestamp(0) with time zone,
  bad timestamp(0) without time zone,

  bad time(0),
  bad time(0) with time zone,
  bad time(0) without time zone
);
