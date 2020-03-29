CREATE TABLE `{2}`
(
    ir_uid        BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    ir_ingredient BIGINT UNSIGNED NOT NULL,
    ir_recipe     BIGINT UNSIGNED NOT NULL,
    ir_weight     FLOAT(5),
    FOREIGN KEY (ir_ingredient) REFERENCES `{3}` (ingredient_uid),
    FOREIGN KEY (ir_recipe) REFERENCES `{4}` (recipe_uid)
) ENGINE = INNODB