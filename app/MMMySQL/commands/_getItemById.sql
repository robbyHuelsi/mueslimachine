CREATE
    DEFINER = '{db_user}'@'{db_host}'
    PROCEDURE `{table}_getItemById`(IN inItemId BIGINT UNSIGNED)
BEGIN
    SELECT *
    FROM `{table}`
    WHERE `{table}_uid` = inItemId;
END;