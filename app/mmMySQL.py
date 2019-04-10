from flaskext.mysql import MySQL
from werkzeug import check_password_hash
import threading
import time

def constant(f):
	def fset(self, value):
		raise TypeError
	def fget(self):
		return f()
	return property(fget, fset)

class _Const(object):
	@constant
	def TBL_USERS():
		return "tbl_users"
	@constant
	def TBL_TUBES():
		return "tbl_tubes"
	@constant
	def TBL_INGREDIENTS():
		return "tbl_ingredients"
	@constant
	def TBL_RECIPES():
		return "tbl_recipes"
	@constant
	def TBL_IR():
		return "tbl_ingredients_recipes"
	
	@constant
	def TABLES():
		CONST = _Const()
		return [CONST.TBL_USERS, CONST.TBL_TUBES, CONST.TBL_INGREDIENTS, CONST.TBL_RECIPES, CONST.TBL_IR]


class mmMySQL():
	def __init__(self, logger, flask, mmStatus, user, password, host, port, dbName):
		self.logger = logger
		self.mmStatus = mmStatus

		self.connection = None

		CONST = _Const()
		self.setStatus(0) # 0 => disconnected / 1 => connecting / 2 => setting up / 3 => connected
		self.mysql = MySQL()
		flask.config['MYSQL_DATABASE_HOST'] = host
		flask.config['MYSQL_DATABASE_PORT'] = port
		flask.config['MYSQL_DATABASE_USER'] = user
		flask.config['MYSQL_DATABASE_PASSWORD'] = password
		
		self.mysql.init_app(flask)
		
		connectingThread = threading.Thread(target=self.connect, args=[CONST, dbName, user, host])
		connectingThread.daemon = True 
		connectingThread.start()
		
	def __del__(self):
		if self.status == 2 or self.status == 3:
			self.connection.close()
			self.logger.log("MySQL connection closed")

	def connect(self, CONST, dbName, user, host):
		if self.status == 1:
			self.logger.logErr("Another thread is trying to connect to database")
			return False
		elif self.status == 2 or self.status == 3:
			self.logger.logErr("Database is already connected")
			return False
		elif self.status == 0:
			self.setStatus(1)
			# In case MySQL is not up yet try to connect every 5 seconds
			while True:
				try:
					self.connection = self.mysql.connect()
					break
				except Exception as e:
					self.logger.logWarn(str(e), flush=True)
					self.logger.log("Wait 5 seconds and try again.", flush=True)
					time.sleep(5)
			self.setStatus(2)
			self.cursor = self.connection.cursor()		
			self.__checkAndSetUpDB(CONST, dbName)
			self.__checkAndSetUpTables(CONST, user, host)
			self.setStatus(3)
			self.logger.log("Database connected", flush=True)
			return True
		else:
			self.logger.logErr("Something went wrong while connecting database")
			return False

	def setStatus(self, status):
		# 0 => disconnected / 1 => connecting / 2 => setting up / 3 => connected
		self.status = status
		self.mmStatus.setDatabaseStatus(status)
		return True
	
	def __checkAndSetUpDB(self, CONST, dbName):
		self.cursor.execute("SHOW DATABASES")
		dbExists = 0
		for (database) in self.cursor:
			if database[0] == dbName:
				dbExists = 1
				break
		if dbExists:
			self.cursor.execute('USE ' + dbName)
			self.logger.log("Database '" + dbName + "' already exists")
		else:  
			self.cursor.execute("create database if not exists " + dbName + " DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci")
			self.cursor.execute('USE ' + dbName)
			self.logger.log("Database '" + dbName + "' was created")
			
	def __checkAndSetUpTables(self, CONST, user, host):
		self.cursor.execute("SHOW TABLES")
		searchTables = self.cursor.fetchall()
				
		for table in CONST.TABLES:
			tblExists = 0
			for (searchTable,) in searchTables:
				if searchTable == table:
					tblExists = 1
					break
					
			if tblExists:
				self.logger.log("Table '" + table + "' already exists")
			else:
				if table == CONST.TBL_USERS:
					self.cursor.execute("CREATE TABLE " + table + " (" +
										"user_uid BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY, " 
										"user_username VARCHAR(20), " +
										"user_firstname VARCHAR(50), " +
										"user_lastname VARCHAR(50), " +
										"user_password VARCHAR(100), " +
										"user_email VARCHAR(50), " +
										"user_role ENUM('pending', 'user', 'admin') NOT NULL DEFAULT 'pending', " +
										"user_regdate TIMESTAMP, " +
										"user_tracking VARCHAR(32500)) ENGINE=INNODB;")
					
					self.cursor.execute("CREATE DEFINER='" + user + "'@'" + host + "' PROCEDURE `sp_users_createUser`(" +
										"IN inUsername VARCHAR(20), " +
										"IN inFirstname VARCHAR(50), " +
										"IN inLastname VARCHAR(50), " +
										"IN inPassword VARCHAR(100), " +
										"IN inEmail VARCHAR(20), " +
										"IN inRole ENUM('pending', 'user', 'admin')) " +
										"BEGIN " +
										"if ( select exists (select 1 from " + CONST.TBL_USERS + " where user_username = inUsername) ) THEN " +
										"select 'Username Exists !!'; " +
										"ELSE " +
										"insert into " + CONST.TBL_USERS + " (user_username, user_firstname, user_lastname, user_password, user_email, user_role) " +
										"values (inUsername, inFirstname, inLastname, inPassword, inEmail, inRole); " +
										"END If; " +
										"END;")
					
					self.cursor.execute("CREATE DEFINER='" + user + "'@'" + host + "' PROCEDURE `spUsers_getPassword`(" +
										"IN inUsername VARCHAR(20)) " +
										"BEGIN " +
										"select user_password from " + CONST.TBL_USERS + " where user_username = inUsername; " +
										"END;")
					
				elif table == CONST.TBL_TUBES:
					self.cursor.execute("CREATE TABLE " + table + " (tube_uid BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY, tube_gpio_1 INT(3) UNSIGNED NOT NULL, tube_gpio_2 INT(3) UNSIGNED NOT NULL) ENGINE=INNODB;")
				elif table == CONST.TBL_INGREDIENTS:
					self.cursor.execute("CREATE TABLE " + table + " (ingredient_uid BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY, ingredient_name VARCHAR(20), ingredient_price FLOAT(5), ingredient_tube BIGINT UNSIGNED NOT NULL, ingredient_glutenfree BOOL, ingredient_lactosefree BOOL, ingredient_motortuning FLOAT(5), FOREIGN KEY (ingredient_tube) REFERENCES " + CONST.TBL_TUBES + "(tube_uid)) ENGINE=INNODB;")
				elif table == CONST.TBL_RECIPES:
					self.cursor.execute("CREATE TABLE " + table + " (recipe_uid BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY, recipe_name VARCHAR(20), recipe_creator BIGINT UNSIGNED NOT NULL, FOREIGN KEY (recipe_creator) REFERENCES " + CONST.TBL_USERS + "(user_uid)) ENGINE=INNODB;")
				elif table == CONST.TBL_IR:
					self.cursor.execute("CREATE TABLE " + table + " (ir_uid BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY, ir_ingredient BIGINT UNSIGNED NOT NULL, ir_recipe BIGINT UNSIGNED NOT NULL, ir_weight FLOAT(5), FOREIGN KEY (ir_ingredient) REFERENCES tbl_ingredients(ingredient_uid), FOREIGN KEY (ir_recipe) REFERENCES " + CONST.TBL_RECIPES + "(recipe_uid)) ENGINE=INNODB;")
				self.logger.log("Table '" + table + "' was created")
				
	
	def spUsersCreateUser(self, inUsername, inFirstname, inLastname, inPassword, inEmail, inRole):
		self.cursor.callproc('sp_users_createUser',(inUsername, inFirstname, inLastname, inPassword, inEmail, inRole))
		data = self.cursor.fetchall()
	
		if len(data) is 0:
			self.connection.commit()
			self.status.addOneTimeNotificationSuccess("User created successfully")
			return "done"
		else:
			self.status.addOneTimeNotificationError("Error while creating new user: " + str(data[0]))
			return "error"

	def spUsersCheckUserPassword(self, inUsername, inPassword):
		self.cursor.callproc('spUsers_getPassword',(inUsername,))
		hashedPassword = self.cursor.fetchall()
		#self.logger.log("Username: " + inUsername)
		#self.logger.log("Password: " + inPassword)
		#self.logger.log("HashedPw: " + str(hashedPassword))
		if hashedPassword:
			return check_password_hash(hashedPassword[0][0], inPassword)
		
		
		
		