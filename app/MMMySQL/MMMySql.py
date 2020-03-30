from flaskext.mysql import MySQL
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
        return [CONST.TBL_USER, CONST.TBL_TUBE, CONST.TBL_INGREDIENT, CONST.TBL_RECIPE, CONST.TBL_IR]


class MMMySql:
    def __init__(self, logger, flask, mm_status, user, password, host, port, db_name):
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

        self.commander = MMMySqlCommander(db_name, user, host, self.CONST_TBL_NAMES)

        connecting_thread = threading.Thread(target=self.connect, args=[db_name, user, host])
        connecting_thread.daemon = True
        connecting_thread.start()

    def __del__(self):
        if self.status == 2 or self.status == 3:
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
            self.cursor = self.connection.cursor()
            self.__check_and_set_up_db(db_name)
            self.__check_and_set_up_tables(user, host)
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
        db_exists = 0
        for (database) in self.cursor:
            if database[0] == db_name:
                db_exists = 1
                break
        if db_exists:
            self.cursor.execute("USE " + db_name)
            self.logger.log("Database '" + db_name + "' already exists")
        else:
            self.cursor.execute(self.commander.get_sql_command("_createDatabase"))
            self.cursor.execute("USE " + db_name)
            self.logger.log("Database '" + db_name + "' was created")

    def __check_and_set_up_tables(self, user, host):
        self.cursor.execute("SHOW TABLES")
        search_tables = self.cursor.fetchall()

        for table in self.CONST_TBL_NAMES.TABLES:
            tbl_exists = 0
            for (searchTable,) in search_tables:
                if searchTable == table:
                    tbl_exists = 1
                    break

            if tbl_exists:
                self.logger.log("Table '" + table + "' already exists")
            else:
                self.cursor.execute(self.commander.get_sql_command(table+"_createTable", table))
                self.cursor.execute(self.commander.get_sql_command("_getItems", table))
                self.cursor.execute(self.commander.get_sql_command("_getItemById", table))
                self.cursor.execute(self.commander.get_sql_command("_deleteItemById", table))

                if table == self.CONST_TBL_NAMES.TBL_USER:
                    self.cursor.execute(self.commander.get_sql_command(table+"_addItem", table))
                    self.cursor.execute(self.commander.get_sql_command(table+"_getPassword", table))

                elif table == self.CONST_TBL_NAMES.TBL_TUBE:
                    self.cursor.execute(self.commander.get_sql_command(table+"_addItem", table))

                elif table == self.CONST_TBL_NAMES.TBL_INGREDIENT:
                    self.cursor.execute(self.commander.get_sql_command(table+"_addItem", table))

                elif table == self.CONST_TBL_NAMES.TBL_RECIPE:
                    pass
                elif table == self.CONST_TBL_NAMES.TBL_IR:
                    pass

                self.logger.log("Table '" + table + "' was created")

    def user_check_user_password(self, in_username, in_password):
        self.cursor.callproc("user_getPassword", (in_username,))
        hashed_password = self.cursor.fetchall()
        # self.logger.log("Username: " + in_username)
        # self.logger.log("Password: " + in_password)
        # self.logger.log("HashedPw: " + str(hashed_password))
        if hashed_password:
            return sec.check_password_hash(hashed_password[0][0], in_password)

    def get_items(self, table):
        if table in self.CONST_TBL_NAMES.TABLES:
            self.cursor.callproc(table + "_getItems", ())
            items = self.cursor.fetchall()
            # self.logger.log("All items of table " + table + ":", flush = True)
            # self.logger.log(str(items), flush = True)
            return items

    def get_item_by_id(self, table, item_id):
        if table in self.CONST_TBL_NAMES.TABLES:
            self.cursor.callproc(table + "_getItemById", (item_id,))
            # self.logger.log("Item " + str(item_id) + " of table " + table + ":", flush = True)
            item = self.cursor.fetchall()
            # self.logger.log(str(item), flush = True)
            return item

    def add_item(self, table, properties):
        # Exit with error, if table is unknown
        if table not in self.CONST_TBL_NAMES.TABLES:
            return False, None, "table_unknown;"

        # Exit with error, if properties doesn't match to requirements.
        # Patch properties if possible (e.g. hash the password).
        approved, properties, err_msg = self.check_and_patch_properties(table, properties)
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
        elif len(data) == 0 or len(data[0]) == 0 or data[0][0] == "item_exists":
            return False, None, "Item already exists."
        elif len(data) == 0 or len(data[0]) == 0 or data[0][0] == "tube_in_use":
            return False, None, "Chosen tube is already assigned."

        # Exit with ID of new item, if everything went well
        self.connection.commit()
        return True, data[0][0], ""

    def edit_item_by_id(self, table, item_id, data):
        if table in self.CONST_TBL_NAMES.TABLES:
            self.cursor.callproc(table + "_getItemById", (item_id,))
            item = self.cursor.fetchall()
            if len(item) == 1:
                # TODO: Implement editing item (Take care at user: password!)
                # self.cursor.callproc(table + "_editItemById",(item_id,...))
                # return True
                return False
            else:
                return False

    def delete_item_by_id(self, table, item_id):
        if table in self.CONST_TBL_NAMES.TABLES:
            self.cursor.callproc(table + "_getItemById", (item_id,))
            item = self.cursor.fetchall()
            if len(item) == 1:
                self.cursor.callproc(table + "_deleteItemById", (item_id,))
                return True
            else:
                return False

    def check_and_patch_properties(self, table, properties):
        success = True
        err_msg = ""
        if table == self.CONST_TBL_NAMES.TBL_USER:
            username, first_name, last_name, password, email, role = properties
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
            else:
                password = sec.generate_password_hash(password)

            properties = (username, first_name, last_name, password, email, role)  # TODO: Do further checks

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
