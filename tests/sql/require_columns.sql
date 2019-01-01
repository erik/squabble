-- enable:RequireColumns required="created_at,timestamp with time zone","updated_at"
-- >>> {"line": 10, "column": 13, "message_id": "MissingRequiredColumn", "message_params": {"tbl": "missing_columns", "col": "updated_at"}}
-- >>> {"line": 15, "column": 2, "message_id": "ColumnWrongType", "message_params": {"tbl": "type_mismatch", "col": "created_at", "actual": "integer", "required": "timestamp with time zone"}}

CREATE TABLE has_all_columns(
  created_at timestamp with time zone,
  updated_at timestamp with time zone
);

CREATE TABLE missing_columns(
  created_at timestamp with time zone
);

CREATE TABLE type_mismatch(
  created_at integer,
  updated_at timestamp with time zone
);
