-- enable:RequirePrimaryKey
-- >>> 14 13 missing_primary_key

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
