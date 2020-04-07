CREATE TABLE `{table}`
(
    recipe_uid     BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    recipe_name    VARCHAR(20)     NOT NULL,
    recipe_creator BIGINT UNSIGNED NOT NULL,
    FOREIGN KEY (recipe_creator) REFERENCES `{tbl_user}` (user_uid)
) ENGINE = INNODB