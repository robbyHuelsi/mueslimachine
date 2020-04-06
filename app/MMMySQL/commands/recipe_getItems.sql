CREATE
    DEFINER = '{db_user}'@'{db_host}'
    PROCEDURE `{tbl_recipe}_getItems`()
BEGIN
    SELECT *
    FROM `{tbl_recipe}`
        INNER JOIN `{tbl_user}` ON {tbl_recipe}.recipe_creator = {tbl_user}.user_uid;
END;