CREATE
    DEFINER = '{0}'@'{1}'
    PROCEDURE `{2}_getItems`()
BEGIN
    SELECT * FROM `{2}`;
END;