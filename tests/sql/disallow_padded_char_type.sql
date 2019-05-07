-- enable:DisallowPaddedCharType
-- >>> {"line": 13, "column": 2, "message_id": "WastefulCharType"}
-- >>> {"line": 14, "column": 2, "message_id": "WastefulCharType"}
-- >>> {"line": 22, "column": 13, "message_id": "WastefulCharType"}
-- >>> {"line": 23, "column": 13, "message_id": "WastefulCharType"}


CREATE TABLE foo (
  good text,
  good varchar,
  good varchar(3),

  bad char,
  bad char(3)
);

ALTER TABLE foo
  ADD COLUMN good text,
  ADD COLUMN good varchar,
  ADD COLUMN good varchar(3),

  ADD COLUMN bad char,
  ADD COLUMN bad char(3);
