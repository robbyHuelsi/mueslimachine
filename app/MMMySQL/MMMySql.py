import os

from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
from werkzeug import security as sec
import threading
import time

from MMMySQL.MMMySQLCommander import MMMySqlCommander


def constant(f):
    def fset(self, value):
        raise TypeError

    def fget(self):
        return f(self)

    return property(fget, fset)


class _ConstTableNames(object):
    @constant
    def TBL_SETTING(self):
        return "setting"

    @constant
    def TBL_USER(self):
        return "user"

    @constant
    def TBL_TUBE(self):
        return "tube"

    @constant
    def TBL_INGREDIENT(self):
        return "ingredient"

    @constant
    def TBL_RECIPE(self):
        return "recipe"

    @constant
    def TBL_IR(self):
        return "ir"

    @constant
    def TABLES(self):
        CONST = _ConstTableNames()
        return [CONST.TBL_SETTING, CONST.TBL_USER, CONST.TBL_TUBE, CONST.TBL_INGREDIENT, CONST.TBL_RECIPE, CONST.TBL_IR]


class MMMySql:
    def __init__(self, logger, flask, mm_status, user, password, host, port, db_name,
                 connect_parallelized=True):
        self.logger = logger
        self.mm_status = mm_status
        self.status = None

        self.connection = None

        self.CONST_TBL_NAMES = _ConstTableNames()
        self.set_status(0)  # 0 => disconnected / 1 => connecting / 2 => setting up / 3 => connected
        self.cursor = None
        self.mysql = MySQL()
        flask.config["MYSQL_DATABASE_HOST"] = host
        flask.config["MYSQL_DATABASE_PORT"] = port
        flask.config["MYSQL_DATABASE_USER"] = user
        flask.config["MYSQL_DATABASE_PASSWORD"] = password

        self.mysql.init_app(flask)

        self.cmder = MMMySqlCommander(db_name, user, host, self.CONST_TBL_NAMES)

        if connect_parallelized:
            connecting_thread = threading.Thread(target=self.connect, args=[db_name, user, host])
            connecting_thread.daemon = True  # Kill thread when main thread is killed
            connecting_thread.start()
        else:
            self.connect(db_name, user, host)

    def __del__(self):
        if self.status in [2, 3]:
            self.connection.close()
            self.logger.log("MySQL connection closed")

    def connect(self, db_name, user, host):
        if self.status == 1:
            self.logger.log_error("Another thread is trying to connect to database")
            return False
        elif self.status == 2 or self.status == 3:
            self.logger.log_error("Database is already connected")
            return False
        elif self.status == 0:
            self.set_status(1)
            # In case MySQL is not up yet try to connect every 5 seconds
            while True:
                try:
                    self.connection = self.mysql.connect()
                    break
                except Exception as e:
                    self.logger.log_warn(str(e), flush=True)
                    self.logger.log("Wait 5 seconds and try again.", flush=True)
                    time.sleep(5)
            self.set_status(2)
            self.cursor = self.connection.cursor(cursor=DictCursor)
            self.__check_and_set_up_db(db_name)
            self.__check_and_set_up_tables(user, host)
            self.__check_and_set_up_entries(user, host)
            self.set_status(3)
            self.logger.log("Database connected", flush=True)
            return True
        else:
            self.logger.log_error("Something went wrong while connecting database")
            return False

    def set_status(self, status):
        # 0 => disconnected / 1 => connecting / 2 => setting up / 3 => connected
        self.status = status
        self.mm_status.set_database_status(status)
        return True

    def __check_and_set_up_db(self, db_name):
        self.cursor.execute("SHOW DATABASES")
        db_exists = False
        for (database) in self.cursor:
            if database['Database'] == db_name:
                db_exists = True
                break
        if db_exists:
            self.cursor.execute("USE " + db_name)
            self.logger.log("Database '" + db_name + "' already exists")
        else:
            self.cmder.execute_sql_cmd(self.cursor, self.cmder.get_sql_cmd("createDatabase"))
            self.cursor.execute("USE " + db_name)
            self.logger.log("Database '" + db_name + "' was created")

    def __check_and_set_up_tables(self, user, host):
        self.cursor.execute("SHOW TABLES")
        search_tables = self.cursor.fetchall()
        self.logger.log(str(search_tables))
        for table in self.CONST_TBL_NAMES.TABLES:
            tbl_exists = 0
            for searchTable in search_tables:
                if searchTable['Tables_in_mm_db'] == table:
                    tbl_exists = 1
                    break

            if tbl_exists:
                self.logger.log("Table '" + table + "' already exists")
            else:
                # Add general procedures
                procedures = ['createTable', 'addItem', 'getItems', 'getItemById', 'deleteItemById', 'updateItemById']
                for procedure in procedures:
                    self.cmder.execute_sql_cmd(self.cursor, self.cmder.get_sql_cmd(procedure, table))

                # Add specific procedures
                if table == self.CONST_TBL_NAMES.TBL_SETTING:
                    self.cmder.execute_sql_cmd(self.cursor, self.cmder.get_sql_cmd('getValueByKey', table))
                    self.cmder.execute_sql_cmd(self.cursor, self.cmder.get_sql_cmd('updateValueByKey', table))

                elif table == self.CONST_TBL_NAMES.TBL_USER:
                    self.cmder.execute_sql_cmd(self.cursor, self.cmder.get_sql_cmd('getUserByUsername', table))

                elif table == self.CONST_TBL_NAMES.TBL_TUBE:
                    pass

                elif table == self.CONST_TBL_NAMES.TBL_INGREDIENT:
                    pass

                elif table == self.CONST_TBL_NAMES.TBL_RECIPE:
                    pass
                elif table == self.CONST_TBL_NAMES.TBL_IR:
                    self.cmder.execute_sql_cmd(self.cursor, self.cmder.get_sql_cmd('getIngredientsByRecipeId', table))

                self.logger.log("Table '" + table + "' was created")

    def __check_and_set_up_entries(self, user, host):
        self.logger.log('__check_and_set_up_entries')
        # Check count users and enter setup mode if necessary
        users = self.get_items(self.CONST_TBL_NAMES.TBL_USER)
        setup_mode_necessary = True
        if users:
            for user in users:
                if user['user_role'] == 'admin':
                    setup_mode_necessary = False
                    self.logger.log('Admin user found')
                    break
        is_setup_mode = self.setting_is_setup_mode()
        if setup_mode_necessary and not is_setup_mode:
            self.logger.log('set setup mode to TRUE, because NO admin user found')
            self.setting_update_value_by_key('setup_mode', 'true')
        elif not setup_mode_necessary and is_setup_mode:
            self.logger.log('set setup mode to FALSE, because AN admin user found')
            self.setting_update_value_by_key('setup_mode', 'false')

    def get_items(self, table):
        if self.status in [0, 1]:
            return False
        if table not in self.CONST_TBL_NAMES.TABLES:
            return False
        self.cursor.callproc(table + "_getItems", ())
        items = self.cursor.fetchall()
        # self.logger.log("All items of table " + table + ":", flush = True)
        # self.logger.log(str(items), flush = True)
        return items

    def get_item_by_id(self, table, item_id):
        if self.status in [0, 1]:
            return False
        if table not in self.CONST_TBL_NAMES.TABLES:
            return False
        self.cursor.callproc(table + "_getItemById", (item_id,))
        # self.logger.log("Item " + str(item_id) + " of table " + table + ":", flush = True)
        item = self.cursor.fetchall()
        # self.logger.log(str(item), flush = True)
        return item

    def add_or_edit_item(self, table, form_input):
        cmd = form_input["cmd"]

        # Fetch columns of this table
        self.cursor.execute("SHOW columns FROM " + table)
        columns = self.cursor.fetchall()
        columns = [c['Field'] for c in columns]

        # Delete uid property if 'add' mode
        if cmd == 'add':
            columns.remove(table + '_uid')

        # Modify column list for special purposes
        if cmd == 'add':
            if table == self.get_tbl_names().TBL_USER:
                columns.remove('user_tracking')
                columns.remove('user_login_date')
                columns.remove('user_reg_date')
                columns.append('user_password_confirm')
        elif cmd == 'edit':
            if table == self.get_tbl_names().TBL_USER:
                columns.remove('user_password')
                columns.remove('user_tracking')
                columns.remove('user_login_date')
                columns.remove('user_reg_date')

        self.logger.log("Columns: " + str(columns))

        # Get properties from user input
        properties = {}
        for column in columns:
            if column in form_input:
                properties[column] = form_input[column]
            else:
                # Modify input for special purposes
                if table == self.get_tbl_names().TBL_USER:
                    if column == 'user_role':
                        properties[column] = 'user'
                elif table == self.get_tbl_names().TBL_INGREDIENT:
                    if column in ['ingredient_glutenfree', 'ingredient_lactosefree']:
                        properties[column] = False
                    elif column == 'ingredient_motortuning':
                        properties[column] = 0
                elif table == self.get_tbl_names().TBL_RECIPE:
                    if column == 'recipe_draft':
                        properties[column] = False

        # Modify properties for special purposes
        for key, val in properties.items():
            if table == self.get_tbl_names().TBL_INGREDIENT:
                if key in ['ingredient_glutenfree', 'ingredient_lactosefree']:
                    properties[key] = True if val == 'true' else False
            elif table == self.get_tbl_names().TBL_RECIPE:
                if key == 'recipe_draft':
                    properties[key] = True if val == 'true' else False

        self.logger.log("Properties: " + str(properties))
        self.logger.log("Count of prop.: " + str(len(properties)))

        if len(properties) != len(columns):
            err_msg = 'Length of properties is unequal to length of table columns'
            self.logger.log(err_msg)
            return False, None, err_msg

        # Add or edit item
        if cmd == 'add':
            success, item_id, err_msg = self.add_item(table, list(properties.values()))
        elif cmd == "edit":
            if (table + '_uid') in properties:
                item_id = properties[table + '_uid']
                success, err_msg = self.edit_item_by_id(table, item_id, list(properties.values()))
        else:
            return False, None, 'Wrong command'

        # For Recipe: Modify IR table
        if success and table == self.get_tbl_names().TBL_RECIPE:
            new_ir_id_list = []
            for key, value in form_input.items():
                if key[0:5] == 'irId_':
                    order = key[5:]
                    ir_id = value
                    ingredient_id = form_input.get("ingredientId_{}".format(order))
                    amount = form_input.get("amount_{}".format(order))
                    if ir_id == '':  # add IR
                        ing_properties = (ingredient_id, item_id, amount, order)
                        ir_success, ir_id, ir_err_msg = self.add_item(self.get_tbl_names().TBL_IR, ing_properties)
                    else:  # edit IR
                        ing_properties = (ir_id, ingredient_id, item_id, amount, order)
                        ir_success, ir_err_msg = self.edit_item_by_id(self.get_tbl_names().TBL_IR, ir_id, ing_properties)
                    if not ir_success:
                        success = False
                        err_msg = 'IR_UID {}: {}'.format(ir_id, ir_err_msg)
                        break
                    new_ir_id_list.append(int(ir_id))

            # In edit mode check if some IR entries have to delete
            if cmd == 'edit':
                ir_list = self.ir_get_ingredients_by_recipe_id(item_id)
                if ir_list:
                    for ir in ir_list:
                        # self.logger.log('{} <-> {}'.format(ir['ir_uid'], new_ir_id_list))
                        if ir['ir_uid'] not in new_ir_id_list:
                            self.logger.log('IR #{} deleted'.format(ir['ir_uid']))
                            self.delete_item_by_id(self.CONST_TBL_NAMES.TBL_IR, ir['ir_uid'])

        return success, item_id, err_msg

    def add_item(self, table, properties):
        if self.status in [0, 1]:
            return False, None, 'database not connected'
        # Exit with error, if table is unknown
        if table not in self.CONST_TBL_NAMES.TABLES:
            return False, None, "table_unknown;"

        # Exit with error, if properties doesn't match to requirements.
        # Patch properties if possible (e.g. hash the password).
        approved, properties, err_msg = self.check_and_patch_properties(table, 'add', properties)
        if not approved:
            return False, None, err_msg

        # Try to add Item and get response
        self.cursor.callproc(table + "_addItem", properties)
        data = self.cursor.fetchall()
        self.logger.log("properties: " + str(properties))
        self.logger.log("data: " + str(data))

        # Exit with error, if adding failed
        if len(data) == 0 or len(data[0]) == 0:
            return False, None, "failed;"
        elif len(data) == 0 or len(data[0]) == 0 or 'item_exists' in data[0]:
            return False, None, "Item already exists."
        elif len(data) == 0 or len(data[0]) == 0 or 'tube_in_use' in data[0]:
            return False, None, "Chosen tube is already assigned."

        # Exit with ID of new item, if everything went well
        self.connection.commit()
        return True, data[0]['LAST_INSERT_ID()'], ""

    def edit_item_by_id(self, table, item_id, properties):
        if self.status in [0, 1]:
            return False, 'database not connected'

        if table not in self.CONST_TBL_NAMES.TABLES:
            return False, "table_unknown;"

        self.cursor.callproc(table + "_getItemById", (item_id,))
        item = self.cursor.fetchall()
        if len(item) != 1:
            return False, "item_does_not_exist;"

        # Exit with error, if properties doesn't match to requirements.
        # Patch properties if possible (e.g. hash the password).
        approved, properties, err_msg = self.check_and_patch_properties(table, 'edit', properties)
        if not approved:
            return False, err_msg

        self.cursor.callproc(table + "_updateItemById", properties)
        return True, ''

    def delete_item_by_id(self, table, item_id):
        if self.status in [0, 1]:
            return False
        if table not in self.CONST_TBL_NAMES.TABLES:
            return False
        self.cursor.callproc(table + "_getItemById", (item_id,))
        item = self.cursor.fetchall()
        if len(item) == 1:
            if table == self.CONST_TBL_NAMES.TBL_RECIPE:
                ir_list = self.ir_get_ingredients_by_recipe_id(item_id)
                if ir_list:
                    for ir in ir_list:
                        self.delete_item_by_id(self.CONST_TBL_NAMES.TBL_IR, ir['ir_uid'])
            self.cursor.callproc(table + "_deleteItemById", (item_id,))
            return True
        else:
            return False

    def setting_get_value_by_key(self, in_key):
        if self.status in [0, 1]:
            return False
        self.cursor.callproc(self.CONST_TBL_NAMES.TBL_SETTING + '_getValueByKey', (in_key,))
        item = self.cursor.fetchall()
        self.logger.log(str(item), flush=True)
        if len(item) == 0:
            return False
        else:
            return item[0]

    def setting_update_value_by_key(self, in_key, in_value):
        if self.status in [0, 1]:
            return False
        self.cursor.callproc(self.CONST_TBL_NAMES.TBL_SETTING + '_updateValueByKey', (in_key, in_value,))
        self.connection.commit()
        # item = self.cursor.fetchall()
        #self.logger.log(str(item), flush=True)
        return True

    def setting_is_setup_mode(self):
        if self.status in [0, 1]:
            return False
        self.cursor.callproc(self.CONST_TBL_NAMES.TBL_SETTING + '_getValueByKey', ('setup_mode',))
        setting_setup_mode = self.cursor.fetchall()
        # self.logger.log(str(setting_setup_mode), flush=True)
        if len(setting_setup_mode) == 0:
            self.add_item(self.CONST_TBL_NAMES.TBL_SETTING, ('setup_mode', 'false'))
            is_setup_mode = False
        else:
            is_setup_mode = setting_setup_mode[0]['setting_value'] == 'true'
        self.logger.log('Setup Mode' if is_setup_mode else 'No Setup Mode')
        return is_setup_mode

    def user_check_user_password(self, in_username, in_password):
        if self.status in [0, 1]:
            return False
        self.cursor.callproc(self.CONST_TBL_NAMES.TBL_USER + "_getUserByUsername", (in_username,))
        user = self.cursor.fetchall()
        if user and len(user) > 0:
            user_uid = user[0]['user_uid']
            hashed_password = user[0]['user_password']
            password_okay = sec.check_password_hash(hashed_password, in_password)
            if password_okay:
                return True, user_uid
        return False, -1

    def ir_get_ingredients_by_recipe_id(self, recipe_id):
        if self.status in [0, 1]:
            return False
        self.cursor.callproc(self.CONST_TBL_NAMES.TBL_IR + "_getIngredientsByRecipeId", (recipe_id,))
        # self.logger.log("Item " + str(item_id) + " of table " + table + ":", flush = True)
        ingredients = self.cursor.fetchall()
        # self.logger.log(str(item), flush = True)
        return ingredients

    def check_and_patch_properties(self, table, cmd, properties):
        success = True
        err_msg = ""
        if table == self.CONST_TBL_NAMES.TBL_SETTING:
            pass  # TODO: Check all properties
        elif table == self.CONST_TBL_NAMES.TBL_USER:
            if cmd == 'add':
                username, first_name, last_name, password, email, role, password_confirm = properties
                uid = True
            elif cmd == 'edit':
                uid, username, first_name, last_name, email, role = properties
                password = True
                password_confirm = True
            else:
                err_msg += "wrong_cmd;"
                return False, properties, err_msg

            if not username:
                success = False
                err_msg += "username_empty;"

            if not email:
                success = False
                err_msg += "email_empty;"

            if not role:
                success = False
                err_msg += "role_empty;"
            elif role not in ["pending", "user", "admin"]:
                success = False
                err_msg += "role_wrong;"

            if not password:
                success = False
                err_msg += "password_empty;"
            elif not password_confirm:
                success = False
                err_msg += "password_conform_empty;"
            elif password != password_confirm:
                success = False
                err_msg += "password_conform_unequal;"
            elif cmd == 'add':
                password = sec.generate_password_hash(password)

            if cmd == 'add':
                properties = (username, first_name, last_name, password, email, role)  # TODO: Do further checks
            elif cmd == 'edit':
                properties = (uid, username, first_name, last_name, email, role)

        elif table == self.CONST_TBL_NAMES.TBL_TUBE:
            pass  # TODO: Check all properties
        elif table == self.CONST_TBL_NAMES.TBL_INGREDIENT:
            pass  # TODO: Check all properties
        elif table == self.CONST_TBL_NAMES.TBL_RECIPE:
            pass  # TODO: Check all properties
        elif table == self.CONST_TBL_NAMES.TBL_IR:
            pass  # TODO: Check all properties

        return success, properties, err_msg

    def get_tbl_names(self):
        return self.CONST_TBL_NAMES
