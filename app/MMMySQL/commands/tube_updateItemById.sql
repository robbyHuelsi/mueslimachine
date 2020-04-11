CREATE
    DEFINER = '{db_user}'@'{db_host}'
    PROCEDURE `{table}_updateItemById`(iN in_uid BIGINT,
                                       IN in_gpio_1 INT,
                                       IN in_gpio_2 INT,
                                       IN in_gpio_3 INT,
                                       IN in_gpio_4 INT)
BEGIN
    UPDATE `{table}`
    SET tube_gpio_1 = in_gpio_1,
        tube_gpio_2 = in_gpio_2,
        tube_gpio_3 = in_gpio_3,
        tube_gpio_4 = in_gpio_4
    WHERE tube_uid = in_uid;
END;