CREATE TABLE `{table}`(
    tube_uid BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    tube_gpio_1 INT UNSIGNED NOT NULL,
    tube_gpio_2 INT UNSIGNED NOT NULL,
    tube_gpio_3 INT UNSIGNED NOT NULL,
    tube_gpio_4 INT UNSIGNED NOT NULL
) ENGINE=INNODB