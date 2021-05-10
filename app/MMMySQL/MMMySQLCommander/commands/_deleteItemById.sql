CREATE
    DEFINER = '{db_user}'@'{db_host}'
    PROCEDURE `{table}_deleteItemById`(IN inItemId BIGINT UNSIGNED)
BEGIN
    DELETE FROM `{table}` where `{table}_uid` = inItemId;
END;