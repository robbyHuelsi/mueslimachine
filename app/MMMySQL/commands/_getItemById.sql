CREATE
    DEFINER = '{0}'@'{1}'
    PROCEDURE `{2}_getItemById`(IN inItemId BIGINT UNSIGNED)
BEGIN
    SELECT * FROM `{2}` WHERE `{2}_uid` = inItemId;
END;