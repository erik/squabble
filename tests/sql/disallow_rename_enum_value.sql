-- enable:DisallowRenameEnumValue
-- >>> {"message_id": "rename_not_allowed"}

ALTER TYPE this_is_fine ADD VALUE '!!!';
ALTER TYPE this_is_not_fine RENAME VALUE '!!!' TO 'something else';
