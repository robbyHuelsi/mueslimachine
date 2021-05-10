CREATE
    DEFINER = '{db_user}'@'{db_host}'
    PROCEDURE `{table}_addItem`(IN in_gpio_1 INT,
                                IN in_gpio_2 INT,
                                IN in_gpio_3 INT,
                                IN in_gpio_4 INT)
BEGIN
    IF (
        SELECT EXISTS(
                       SELECT 1
                       FROM `{table}`
                       WHERE tube_gpio_1 = in_gpio_1
                          OR tube_gpio_2 = in_gpio_2
                          OR tube_gpio_3 = in_gpio_3
                          OR tube_gpio_4 = in_gpio_4)
    ) THEN
        SELECT 'item_exists';
    ELSE
        INSERT INTO `{table}`(tube_gpio_1,
                              tube_gpio_2,
                              tube_gpio_3,
                              tube_gpio_4)
        VALUES (in_gpio_1,
                in_gpio_2,
                in_gpio_3,
                in_gpio_4);
        SELECT LAST_INSERT_ID();
    END IF;
END;