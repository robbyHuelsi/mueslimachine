CREATE TABLE `{table}`
(
    setting_uid      BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    setting_key      VARCHAR(50)     NOT NULL,
    setting_value    VARCHAR(255),
    setting_reg_date TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    setting_updated  TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE (`setting_uid`, `setting_key`)
) ENGINE = INNODB
