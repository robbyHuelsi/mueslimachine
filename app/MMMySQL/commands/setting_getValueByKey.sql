CREATE
    DEFINER = '{db_user}'@'{db_host}'
    PROCEDURE `{table}_getValueByKey`(IN in_key VARCHAR(20))
BEGIN
    SELECT setting_value
    FROM `{table}`
    WHERE setting_key = in_key;
END;