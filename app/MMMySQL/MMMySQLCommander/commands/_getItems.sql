CREATE
    DEFINER = '{db_user}'@'{db_host}'
    PROCEDURE `{table}_getItems`()
BEGIN
    SELECT * FROM `{table}`;
END;