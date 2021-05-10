CREATE
    DEFINER = '{db_user}'@'{db_host}'
    PROCEDURE `{table}_updateValueByKey`(IN in_key VARCHAR(20), IN in_value VARCHAR(100))
BEGIN
    UPDATE `{table}`
    SET setting_value = in_value
    WHERE setting_key = in_key;
END;