-- enable:RequirePrimaryKey
-- >>> {"line": 14, "column": 13, "message_id": "missing_primary_key"}

CREATE TABLE inline_pk(
  pk int PRIMARY KEY
);

CREATE TABLE inline_pk(
  pk int,

  PRIMARY KEY(pk)
);

CREATE TABLE missing_pk(
  not_pk int
);
