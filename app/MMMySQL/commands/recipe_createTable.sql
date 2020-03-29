CREATE TABLE `{2}`
(
    recipe_uid     BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    recipe_name    VARCHAR(20),
    recipe_creator BIGINT UNSIGNED NOT NULL,
    FOREIGN KEY (recipe_creator) REFERENCES `{3}` (user_uid)
) ENGINE = INNODB