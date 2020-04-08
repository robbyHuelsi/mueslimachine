CREATE
    DEFINER = '{db_user}'@'{db_host}'
    PROCEDURE `{table}_addItem`(IN in_key VARCHAR(50),
                                IN in_value VARCHAR(255))
BEGIN
    INSERT INTO `{table}`(setting_key,
                          setting_value)
    VALUES (in_key,
            in_value);
    SELECT LAST_INSERT_ID();
END;