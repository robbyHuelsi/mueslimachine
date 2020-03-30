CREATE
    DEFINER = '{db_user}'@'{db_host}'
    PROCEDURE `{table}_addItem`(IN in_name VARCHAR(20),
                                IN in_creator VARCHAR(20))
BEGIN
    INSERT INTO `{table}`(recipe_name,
                          recipe_creator)
    VALUES (in_name,
            in_creator);
    SELECT LAST_INSERT_ID();
END;