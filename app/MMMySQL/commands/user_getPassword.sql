CREATE
    DEFINER = '{0}'@'{1}'
    PROCEDURE `{2}_getPassword`(IN in_username VARCHAR(20))
BEGIN
    SELECT user_password
    FROM `{2}`
    WHERE user_username = in_username;
END;