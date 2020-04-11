CREATE
    DEFINER = '{db_user}'@'{db_host}'
    PROCEDURE `{table}_updateItemById`(IN in_uid BIGINT,
                                       IN in_name VARCHAR(50),
                                       IN in_price FLOAT(5),
                                       IN in_tube BIGINT,
                                       IN in_glutenfree BOOL,
                                       IN in_lactosefree BOOL,
                                       IN in_motortuning FLOAT(5))
BEGIN
    UPDATE `{table}`
    SET ingredient_name        = in_name,
        ingredient_price       = in_price,
        ingredient_tube        = in_tube,
        ingredient_glutenfree  = in_glutenfree,
        ingredient_lactosefree = in_lactosefree,
        ingredient_motortuning = in_motortuning
    WHERE ingredient_uid = in_uid;
END;