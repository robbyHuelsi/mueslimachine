CREATE
    DEFINER = '{db_user}'@'{db_host}'
    PROCEDURE `{table}_updateItemById`(IN in_uid BIGINT,
                                       IN in_ingredient BIGINT,
                                       IN in_recipe BIGINT,
                                       IN in_weight FLOAT(5),
                                       IN in_order INT)
BEGIN
    UPDATE `{table}`
    SET ir_ingredient = in_ingredient,
        ir_recipe     = in_recipe,
        ir_weight     = in_weight,
        ir_order      = in_order
    WHERE ir_uid = in_uid;
END;