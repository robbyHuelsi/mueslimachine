from serial import Serial
from datetime import datetime

class mmArduino():
	
	def __init__(self, logger, status, port):
		self.logger = logger
		self.status = status
		self.port = port
		
		self.serial = None
		self.time = None
		self.hasSetup = False

		self.open()
	   
	def __del__(self):
		self.close()

	def open(self):
		try:
			self.serial = Serial(self.port, 300)
			return True
		except Exception as e:
			self.logger.logErr(str(e))
			return False
		self.time = datetime.now()
		self.hasSetup = True #TODO: False

	def close(self):
		if self.serial != None:
			try:
				self.serial.close()
			except Exception as e:
				self.logger.logErr(str(e))
				return False
		self.serial = None
		self.time = None
		self.hasSetup = False
		return True

	def sendInit(self): #TODO: Object mit allen Tubes und ihre Pins als Übergabeparameter
		# TODO: Init ausarbeiten
		# self.serial.write('i\n')
		self.logger.logWarn("Init not implemented!")
		return False

	def sendDrive(self, id, steps) :
		if self.serial == None:
			self.logger.logErr("Serial Port not open")
			return False
		elif self.hasSetup == False:
			self.logger.logErr("Serial Port not set up")
			return False
		else:
			msg = 'd,' + str(id) + ',' + str(steps)
			if self.serial.write(msg + '\n'):
				self.logger.log("Message sent to Arduino: " + msg)
			else:
				self.logger.logErr("Sending message to Arduino failed")
			return True
