CREATE
    DEFINER = '{db_user}'@'{db_host}'
    PROCEDURE `{table}_addItem`(IN in_name VARCHAR(100),
                                IN in_creator BIGINT,
                                IN in_draft BOOL,
                                IN in_description TEXT,
                                IN in_icon VARCHAR(50),
                                IN in_bgcolor1 VARCHAR(50),
                                IN in_bgcolor2 VARCHAR(50))
BEGIN
    INSERT INTO `{table}`(recipe_name,
                          recipe_creator,
                          recipe_draft,
                          recipe_description,
                          recipe_icon,
                          recipe_bgcolor1,
                          recipe_bgcolor2)
    VALUES (in_name,
            in_creator,
            in_draft,
            in_description,
            in_icon,
            in_bgcolor1,
            in_bgcolor2);
    SELECT LAST_INSERT_ID();
END;