CREATE
    DEFINER = '{db_user}'@'{db_host}'
    PROCEDURE `{tbl_ir}_getIngredientsByRecipeId`(IN inRecipeId BIGINT UNSIGNED)
BEGIN
    SELECT *
    FROM `{tbl_ir}`
             INNER JOIN `{tbl_ingredient}` ON {tbl_ir}.ir_ingredient = {tbl_ingredient}.ingredient_uid
    WHERE `ir_recipe` = inRecipeId
    ORDER BY
        ir_order ASC;
END;