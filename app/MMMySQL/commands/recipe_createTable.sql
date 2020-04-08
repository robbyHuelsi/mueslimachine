CREATE TABLE `{table}`
(
    recipe_uid         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    recipe_name        VARCHAR(100)    NOT NULL,
    recipe_creator     BIGINT UNSIGNED NOT NULL,
    recipe_description TEXT,
    recipe_draft       BOOL DEFAULT true,
    FOREIGN KEY (recipe_creator) REFERENCES `{tbl_user}` (user_uid)
) ENGINE = INNODB