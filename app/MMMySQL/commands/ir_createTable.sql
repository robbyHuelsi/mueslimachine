CREATE TABLE `{table}`
(
    ir_uid        BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    ir_ingredient BIGINT UNSIGNED NOT NULL,
    ir_recipe     BIGINT UNSIGNED NOT NULL,
    ir_weight     BIGINT UNSIGNED,
    ir_order      INT UNSIGNED,
    FOREIGN KEY (ir_ingredient) REFERENCES `{tbl_ingredient}` (ingredient_uid),
    FOREIGN KEY (ir_recipe) REFERENCES `{tbl_recipe}` (recipe_uid)
) ENGINE = INNODB