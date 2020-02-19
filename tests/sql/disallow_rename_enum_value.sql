-- squabble-enable:DisallowRenameEnumValue
-- >>> {"message_id": "RenameNotAllowed"}

ALTER TYPE this_is_fine ADD VALUE '!!!';
ALTER TYPE this_is_not_fine RENAME VALUE '!!!' TO 'something else';
