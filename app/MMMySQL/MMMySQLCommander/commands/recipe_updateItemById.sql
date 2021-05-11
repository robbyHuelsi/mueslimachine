CREATE
    DEFINER = '{db_user}'@'{db_host}'
    PROCEDURE `{table}_updateItemById`(in in_uid BIGINT,
                                   IN in_name VARCHAR(100),
                                   IN in_creator BIGINT,
                                   IN in_draft BOOL,
                                   IN in_description TEXT,
                                   IN in_icon VARCHAR(50),
                                   IN in_bgcolor1 VARCHAR(50),
                                   IN in_bgcolor2 VARCHAR(50))
BEGIN
    UPDATE `{table}`
    SET recipe_name = in_name,
        recipe_creator = in_creator,
        recipe_draft = in_draft,
        recipe_description = in_description,
        recipe_icon = in_icon,
        recipe_bgcolor1 = in_bgcolor1,
        recipe_bgcolor2 = in_bgcolor2

    WHERE recipe_uid = in_uid;
END;