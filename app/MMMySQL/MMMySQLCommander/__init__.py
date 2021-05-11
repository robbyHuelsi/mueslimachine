import os.path
from typing import Union

from MMMySQL.TableNames import TableNames


class MMMySqlCommander:
    def __init__(self, db_name, db_user, db_host):
        self.db_name = db_name
        self.db_user = db_user
        self.db_host = db_host

        self.folder_path = os.path.join(os.path.dirname(__file__), 'commands')

    def get_sql_cmd(self, procedure_name, table: Union[TableNames, str] = '', fail_silent=False):
        # Exit with error, if table is unknown
        if type(table) == str and table != '':
            try:
                table = TableNames(table)
            except ValueError:
                if fail_silent:
                    return False
                else:
                    raise Exception('Table unknown.')

        if type(table) == TableNames:
            table = table.value

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
                                                   tbl_user=TableNames.USER.value,
                                                   tbl_tube=TableNames.TUBE.value,
                                                   tbl_ingredient=TableNames.INGREDIENT.value,
                                                   tbl_recipe=TableNames.RECIPE.value,
                                                   tbl_ir=TableNames.IR.value,
                                                   table=table)

    def execute_sql_cmd(self, cursor, command):
        if cursor and command:
            return cursor.execute(command)
        else:
            return False


# if __name__ == '__main__':
#     table_names = MMMySql.TableNames()
#     commander = MMMySqlCommander('mm_db', 'root', 'db', table_names)
#     print(commander.get_sql_cmd('recipe_getItemById', 'user'))
