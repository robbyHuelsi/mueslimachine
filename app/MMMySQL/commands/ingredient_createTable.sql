CREATE TABLE `{table}`
(
    ingredient_uid         BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    ingredient_name        VARCHAR(20),
    ingredient_price       FLOAT(5),
    ingredient_tube        BIGINT UNSIGNED NOT NULL,
    ingredient_glutenfree  BOOL,
    ingredient_lactosefree BOOL,
    ingredient_motortuning FLOAT(5),
    FOREIGN KEY (ingredient_tube) REFERENCES `{tbl_tube}` (tube_uid)
) ENGINE = INNODB