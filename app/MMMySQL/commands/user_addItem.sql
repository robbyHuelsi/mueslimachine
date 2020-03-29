CREATE
    DEFINER = '{0}'@'{1}'
    PROCEDURE `{2}_addItem`(IN in_username VARCHAR(20),
                            IN in_first_name VARCHAR(50),
                            IN in_last_name VARCHAR(50),
                            IN in_password VARCHAR(100),
                            IN in_email VARCHAR(20),
                            IN in_role ENUM ('pending', 'user', 'admin'))
BEGIN
    IF (
        SELECT EXISTS(
                       SELECT 1
                       FROM `{2}`
                       WHERE user_username = in_username
                   )
    ) THEN
        SELECT 'item_exists' ;
    ELSE
        INSERT INTO `{2}`(user_username,
                          user_first_name,
                          user_last_name,
                          user_password,
                          user_email,
                          user_role)
        VALUES (in_username,
                in_first_name,
                in_last_name,
                in_password,
                in_email,
                in_role);
        SELECT LAST_INSERT_ID();
    END IF;
END;