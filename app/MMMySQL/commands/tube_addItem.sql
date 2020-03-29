CREATE
    DEFINER = '{0}'@'{1}'
    PROCEDURE `{2}_addItem`(IN in_gpio_1 INT(3),
                            IN in_gpio_2 INT(3),
                            IN in_gpio_3 INT(3),
                            IN in_gpio_4 INT(3))
BEGIN
    IF (
        SELECT EXISTS(
                       SELECT 1
                       FROM `{2}`
                       WHERE tube_gpio_1 = in_gpio_1
                          OR tube_gpio_2 = in_gpio_2
                          OR tube_gpio_3 = in_gpio_3
                          OR tube_gpio_4 = in_gpio_4)
    ) THEN
        SELECT 'item_exists';
    ELSE
        INSERT INTO `{2}`(tube_gpio_1,
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