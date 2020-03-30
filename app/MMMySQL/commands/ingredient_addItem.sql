CREATE
    DEFINER = '{db_user}'@'{db_host}'
    PROCEDURE `{table}_addItem`(IN in_name VARCHAR(20),
                                IN in_price FLOAT(5),
                                IN in_tube BIGINT,
                                IN in_glutenfree BOOL,
                                IN in_lactosefree BOOL,
                                IN in_motortuning FLOAT(5))
BEGIN
    IF (
        SELECT EXISTS(
                       SELECT 1
                       FROM `{table}`
                       WHERE ingredient_tube = in_tube
                   )
    ) THEN
        SELECT 'tube_in_use';
    ELSE
        INSERT INTO `{table}`(ingredient_name,
                              ingredient_price,
                              ingredient_tube,
                              ingredient_glutenfree,
                              ingredient_lactosefree,
                              ingredient_motortuning)
        VALUES (in_name,
                in_price,
                in_tube,
                in_glutenfree,
                in_lactosefree,
                in_motortuning);
        SELECT LAST_INSERT_ID();
    END IF;
END;