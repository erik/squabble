-- enable:RequireConcurrentIndex
-- >>> {"line": 10, "column": 24, "message_id": "index_not_concurrent"}

CREATE TABLE foo(id uuid);

-- Ok, this is on a new table
CREATE INDEX on foo(id);

-- Not okay, this is not a new table
CREATE INDEX bad_idx on bar(id);

-- Okay, created with CONCURRENTLY
CREATE INDEX CONCURRENTLY on bar(id);
