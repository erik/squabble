-- enable:DisallowNotIn
-- >>> {"line": 8, "column": 17, "message_id": "NotInNotAllowed"}
-- >>> {"line": 12, "column": 9, "message_id": "NotInNotAllowed"}

SELECT abc
FROM xyz
WHERE 1=1
  AND id NOT IN (1, null);

SELECT *
FROM users
WHERE id NOT IN (
  SELECT user_id
  FROM posts
);
