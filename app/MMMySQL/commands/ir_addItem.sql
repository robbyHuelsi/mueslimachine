CREATE
    DEFINER = '{db_user}'@'{db_host}'
    PROCEDURE `{table}_addItem`(IN in_ingredient BIGINT,
                                IN in_recipe     BIGINT,
                                IN in_weight     FLOAT(5),
                                IN in_order      INT)
BEGIN
    INSERT INTO `{table}`(ir_ingredient,
                          ir_recipe,
                          ir_weight,
                          ir_order)
    VALUES (in_ingredient,
            in_recipe,
            in_weight,
            in_order);
    SELECT LAST_INSERT_ID();
END;