CREATE TABLE `{table}`
(
    `user_uid`        BIGINT UNSIGNED                   NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `user_username`   VARCHAR(20)                       NOT NULL,
    `user_first_name` VARCHAR(50),
    `user_last_name`  VARCHAR(50),
    `user_password`   VARCHAR(100)                      NOT NULL,
    `user_email`      VARCHAR(50)                       NOT NULL,
    `user_role`       ENUM ('pending', 'user', 'admin') NOT NULL DEFAULT 'pending',
    `user_tracking`   VARCHAR(100),
    `user_login_date` TIMESTAMP,
    `user_reg_date`   TIMESTAMP                         NOT NULL DEFAULT now(),
    UNIQUE (`user_uid`, `user_username`)
) ENGINE = INNODB