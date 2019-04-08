#!/usr/bin/python
#
import os

from mmFlask.mmFlask import mmFlask
from mmStatus import mmStatus
from mmMySQL import mmMySQL
from mmArduino import mmArduino

# Auskommentiert wg. Docker-Test
# from mmPyDevD import mmPyDevD
# from mmGpio import *
# from mmGpioServo import *

class muesliMachine():
	def __init__(self):
		db_host = os.getenv("DB_HOST", "127.0.0.1")
		db_port = int(os.getenv("DB_PORT", 3306))
		db_user = os.getenv("DB_USER", "root")
		db_pass = os.getenv("DB_PASS", "root")
		db_name = os.getenv("DB_NAME", "mueslimachine")
		arduino_port = os.getenv("ARDUINO_PORT", "/dev/ttyUSB0")

		print(db_host)
		print(db_port)

		self.flask = mmFlask(self)

		self.status = mmStatus()
		self.mySQL = mmMySQL(self.flask, self.status, db_user, db_pass, db_host, db_port, db_name)

		self.arduino = mmArduino(arduino_port, self.status)

		#pyDevD = mmPyDevD() #Eclipse Python Remote Dev Environment

		# Auskommentiert wg. Docker-Test
		#self.ledRed = mmGpioOutBinary(4,0,"LED Red", self.status)
		#self.ledYellow = mmGpioOutBinary(17,0,"LED Yellow", self.status)
		#self.servo1 = mmGpioServo(22, "Servo 1", self.status)

		refUnit = -1026300 / 503

		# Auskommentiert wg. Docker-Test
		#self.scale = mmGpioInHx711(5, 6, "Scale", refUnit, self.status) #(self, pin1, pin2, name, refUnit, mmStatus)

		self.flask.run(debug=True, host='0.0.0.0', port=80)

	
if __name__ == '__main__':
	muesliMachine()