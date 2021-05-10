import os.path


class MMMySqlCommander:
    def __init__(self, db_name, db_user, db_host, tbl_names):
        self.db_name = db_name
        self.db_user = db_user
        self.db_host = db_host
        self.tbl_names = tbl_names

        self.folder_path = os.path.join(os.path.dirname(__file__), 'commands')

    def get_sql_cmd(self, procedure_name, table='', fail_silent=False):

        if os.path.isfile(os.path.join(self.folder_path, table + '_' + procedure_name + '.sql')):
            file_path = os.path.join(self.folder_path, table + '_' + procedure_name + '.sql')
        elif os.path.isfile(os.path.join(self.folder_path, '_' + procedure_name + '.sql')):
            file_path = os.path.join(self.folder_path, '_' + procedure_name + '.sql')
        else:
            if fail_silent:
                return False
            else:
                raise Exception('Command template not found.')

        with open(file_path, "r") as command_file:
            return str(command_file.read()).format(db_name=self.db_name,
                                                   db_user=self.db_user,
                                                   db_host=self.db_host,
                                                   tbl_user=self.tbl_names.TBL_USER,
                                                   tbl_tube=self.tbl_names.TBL_TUBE,
                                                   tbl_ingredient=self.tbl_names.TBL_INGREDIENT,
                                                   tbl_recipe=self.tbl_names.TBL_RECIPE,
                                                   tbl_ir=self.tbl_names.TBL_IR,
                                                   table=table)

    def execute_sql_cmd(self, cursor, command):
        if cursor and command:
            return cursor.execute(command)
        else:
            return False


# if __name__ == '__main__':
#     table_names = MMMySql._ConstTableNames()
#     commander = MMMySqlCommander('mm_db', 'root', 'db', table_names)
#     print(commander.get_sql_cmd('recipe_getItemById', 'user'))
