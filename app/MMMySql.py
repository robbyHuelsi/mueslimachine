from flaskext.mysql import MySQL
from werkzeug import security as sec
import threading
import time


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
        flask.config['MYSQL_DATABASE_HOST'] = host
        flask.config['MYSQL_DATABASE_PORT'] = port
        flask.config['MYSQL_DATABASE_USER'] = user
        flask.config['MYSQL_DATABASE_PASSWORD'] = password

        self.mysql.init_app(flask)

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
            self.cursor.execute('USE ' + db_name)
            self.logger.log("Database '" + db_name + "' already exists")
        else:
            self.cursor.execute("create database if not exists "
                                + db_name + " DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci")
            self.cursor.execute('USE ' + db_name)
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
                if table == self.CONST_TBL_NAMES.TBL_USER:
                    self.cursor.execute("CREATE TABLE " + table + " (" +
                                        "user_uid BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY, " +
                                        "user_username VARCHAR(20), " +
                                        "user_first_name VARCHAR(50), " +
                                        "user_last_name VARCHAR(50), " +
                                        "user_password VARCHAR(100), " +
                                        "user_email VARCHAR(50), " +
                                        "user_role ENUM('pending', 'user', 'admin') NOT NULL DEFAULT 'pending', " +
                                        "user_reg_date TIMESTAMP, " +
                                        "user_tracking VARCHAR(32500)) ENGINE=INNODB;")

                    self.cursor.execute(
                        "CREATE DEFINER='" + user + "'@'" + host + "' PROCEDURE `" + table + "_add_item`(" +
                        "IN in_username VARCHAR(20), " +
                        "IN in_first_name VARCHAR(50), " +
                        "IN in_last_name VARCHAR(50), " +
                        "IN in_password VARCHAR(100), " +
                        "IN in_email VARCHAR(20), " +
                        "IN in_role ENUM('pending', 'user', 'admin')) " +
                        "BEGIN " +
                        "if ( select exists (select 1 from " + table + " where user_username = in_username) ) THEN " +
                        "select 'item_exists'; " +
                        "ELSE " +
                        "insert into " + table +
                        " (user_username, " +
                        "user_first_name, " +
                        "user_last_name, " +
                        "user_password, " +
                        "user_email, " +
                        "user_role) " +
                        "values (in_username, in_first_name, in_last_name, in_password, in_email, in_role); " +
                        "select LAST_INSERT_ID();" +
                        "END If; " +
                        "END;")

                    self.cursor.execute(
                        "CREATE DEFINER='" + user + "'@'" + host + "' PROCEDURE `" + table + "_getPassword`(" +
                        "IN in_username VARCHAR(20)) " +
                        "BEGIN " +
                        "select user_password from " + self.CONST_TBL_NAMES.TBL_USER +
                        " where user_username = in_username; " +
                        "END;")

                elif table == self.CONST_TBL_NAMES.TBL_TUBE:
                    self.cursor.execute("CREATE TABLE " + table + " (" +
                                        "tube_uid BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY, " +
                                        "tube_gpio_1 INT(3) UNSIGNED NOT NULL, " +
                                        "tube_gpio_2 INT(3) UNSIGNED NOT NULL, " +
                                        "tube_gpio_3 INT(3) UNSIGNED NOT NULL, " +
                                        "tube_gpio_4 INT(3) UNSIGNED NOT NULL) ENGINE=INNODB;")

                    self.cursor.execute(
                        "CREATE DEFINER='" + user + "'@'" + host + "' PROCEDURE `" + table + "_add_item`(" +
                        "IN in_gpio_1 INT(3), " +
                        "IN in_gpio_2 INT(3), " +
                        "IN in_gpio_3 INT(3), " +
                        "IN in_gpio_4 INT(3)) " +
                        "BEGIN " +
                        "if(select exists(select 1 from " + table +
                        " where tube_gpio_1 = in_gpio_1 OR " +
                        "tube_gpio_2 = in_gpio_2 OR " +
                        "tube_gpio_3 = in_gpio_3 OR " +
                        "tube_gpio_4 = in_gpio_4)) " +
                        "THEN " +
                        "select 'item_exists'; " +
                        "ELSE " +
                        "insert into " + table + " (tube_gpio_1, tube_gpio_2, tube_gpio_3, tube_gpio_4) " +
                        "values (in_gpio_1, in_gpio_2, in_gpio_3, in_gpio_4); " +
                        "select LAST_INSERT_ID();" +
                        "END If; " +
                        "END;")

                elif table == self.CONST_TBL_NAMES.TBL_INGREDIENT:
                    self.cursor.execute(
                        "CREATE TABLE " + table + " (ingredient_uid BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY, ingredient_name VARCHAR(20), ingredient_price FLOAT(5), ingredient_tube BIGINT UNSIGNED NOT NULL, ingredient_glutenfree BOOL, ingredient_lactosefree BOOL, ingredient_motortuning FLOAT(5), FOREIGN KEY (ingredient_tube) REFERENCES " + self.CONST_TBL_NAMES.TBL_TUBE + "(tube_uid)) ENGINE=INNODB;")
                elif table == self.CONST_TBL_NAMES.TBL_RECIPE:
                    self.cursor.execute(
                        "CREATE TABLE " + table + " (recipe_uid BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY, recipe_name VARCHAR(20), recipe_creator BIGINT UNSIGNED NOT NULL, FOREIGN KEY (recipe_creator) REFERENCES " + self.CONST_TBL_NAMES.TBL_USER + "(user_uid)) ENGINE=INNODB;")
                elif table == self.CONST_TBL_NAMES.TBL_IR:
                    self.cursor.execute(
                        "CREATE TABLE " + table + " (ir_uid BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY, ir_ingredient BIGINT UNSIGNED NOT NULL, ir_recipe BIGINT UNSIGNED NOT NULL, ir_weight FLOAT(5), FOREIGN KEY (ir_ingredient) REFERENCES " + self.CONST_TBL_NAMES.TBL_INGREDIENT + "(ingredient_uid), FOREIGN KEY (ir_recipe) REFERENCES " + self.CONST_TBL_NAMES.TBL_RECIPE + "(recipe_uid)) ENGINE=INNODB;")

                self.cursor.execute(
                    "CREATE DEFINER='" + user + "'@'" + host + "' PROCEDURE `" + table + "_getItems`() " +
                    "BEGIN " +
                    "select * from " + table + "; "
                                               "END;")

                self.cursor.execute(
                    "CREATE DEFINER='" + user + "'@'" + host + "' PROCEDURE `" + table + "_getItemById`(" +
                    "IN inItemId BIGINT UNSIGNED) " +
                    "BEGIN " +
                    "select * from " + table + " where " + table + "_uid = inItemId; " +
                    "END;")

                self.cursor.execute(
                    "CREATE DEFINER='" + user + "'@'" + host + "' PROCEDURE `" + table + "_deleteItemById`(" +
                    "IN inItemId BIGINT UNSIGNED) " +
                    "BEGIN " +
                    "delete from " + table + " where " + table + "_uid = inItemId; " +
                    "END;")

                self.logger.log("Table '" + table + "' was created")

    def user_check_user_password(self, in_username, in_password):
        self.cursor.callproc('user_getPassword', (in_username,))
        hashed_password = self.cursor.fetchall()
        # self.logger.log("Username: " + in_username)
        # self.logger.log("Password: " + in_password)
        # self.logger.log("HashedPw: " + str(hashed_password))
        if hashed_password:
            return sec.check_password_hash(hashed_password[0][0], in_password)

    def get_items(self, table):
        if table in self.CONST_TBL_NAMES.TABLES:
            self.cursor.callproc(table + '_getItems', ())
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
        self.cursor.callproc(table + "_add_item", properties)
        data = self.cursor.fetchall()
        self.logger.log("properties: " + str(properties))
        self.logger.log("data: " + str(data))

        # Exit with error, if adding failed
        if len(data) == 0 or len(data[0]) == 0:
            return False, None, "failed;"
        elif len(data) == 0 or len(data[0]) == 0 or data[0][0] == "item_exists":
            return False, None, "item_exists;"

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
