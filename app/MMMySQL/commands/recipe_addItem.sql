CREATE
    DEFINER = '{db_user}'@'{db_host}'
    PROCEDURE `{table}_addItem`(IN in_name VARCHAR(100),
                                IN in_creator BIGINT,
                                IN in_description TEXT,
                                IN in_draft BOOL)
BEGIN
    INSERT INTO `{table}`(recipe_name,
                          recipe_creator,
                          recipe_description,
                          recipe_draft)
    VALUES (in_name,
            in_creator,
            in_description,
            in_draft);
    SELECT LAST_INSERT_ID();
END;