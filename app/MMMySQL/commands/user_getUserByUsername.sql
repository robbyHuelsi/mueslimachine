CREATE
    DEFINER = '{db_user}'@'{db_host}'
    PROCEDURE `{table}_getUserByUsername`(IN in_username VARCHAR(20))
BEGIN
    SELECT *
    FROM `{table}`
    WHERE user_username = in_username;
END;