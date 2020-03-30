CREATE
    DEFINER = '{db_user}'@'{db_host}'
    PROCEDURE `{table}_getPassword`(IN in_username VARCHAR(20))
BEGIN
    SELECT user_password
    FROM `{table}`
    WHERE user_username = in_username;
END;