CREATE
    DEFINER = '{db_user}'@'{db_host}'
    PROCEDURE `{table}_updateItemById`(IN in_uid BIGINT,
                                       IN in_username VARCHAR(50),
                                       IN in_first_name VARCHAR(100),
                                       IN in_last_name VARCHAR(100),
                                       IN in_email VARCHAR(100),
                                       IN in_role ENUM ('pending', 'user', 'admin'))
BEGIN
    UPDATE `{table}`
    SET user_username = in_username,
        user_first_name = in_first_name,
        user_last_name = in_last_name,
        user_email = in_email,
        user_role = in_role
    WHERE user_uid = in_uid;
END;