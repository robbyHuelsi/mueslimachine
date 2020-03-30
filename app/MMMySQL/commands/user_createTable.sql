CREATE TABLE `{table}`
(
    user_uid        BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_username   VARCHAR(20),
    user_first_name VARCHAR(50),
    user_last_name  VARCHAR(50),
    user_password   VARCHAR(100),
    user_email      VARCHAR(50),
    user_role       ENUM ('pending', 'user', 'admin') NOT NULL DEFAULT 'pending',
    user_reg_date   TIMESTAMP,
    user_tracking   VARCHAR(100)
) ENGINE = INNODB