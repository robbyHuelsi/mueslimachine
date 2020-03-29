import os.path


def get_sql_command(file_name, user, host, table, ref_table_1='', ref_table_2=''):
    file_path = os.path.join(os.path.dirname(__file__), file_name + '.sql')
    with open(file_path, "r") as command_file:
        return str(command_file.read()).format(user, host, table, ref_table_1, ref_table_2)


if __name__ == '__main__':
    print(get_sql_command('user_add_item', 'root', 'db', 'user'))
