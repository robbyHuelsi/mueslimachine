CREATE
    DEFINER = '{0}'@'{1}'
    PROCEDURE `{2}_deleteItemById`(IN inItemId BIGINT UNSIGNED)
BEGIN
    DELETE FROM `{2}` where `{2}_uid` = inItemId;
END;