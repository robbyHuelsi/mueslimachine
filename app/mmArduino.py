from serial import Serial
import threading
import time

class mmArduino():
	
	def __init__(self, logger, status, port):
		self.logger = logger
		self.status = status
		self.port = port
		
		self.connecting = False
		self.connected = False
		self.serial = None
		self.time = None

		connectingThread = threading.Thread(target=self.connect, args=())
		connectingThread.daemon = True 
		connectingThread.start()
	   
	def __del__(self):
		if self.connected:
			self.serial.close()

	def connect(self):
		if self.connecting == True:
			self.logger.logErr("Another thread is trying to connect to Arduino")
			return False
		elif self.connected == True:
			self.logger.logErr("Aduino is already connected")
			return False
		else:
			self.connecting = True
			# In case Arduino is not up yet try to connect every 5 seconds
			while True:
				try:
					self.serial = Serial(self.port, 300)
					# TODO: self.sendPing() ...
					break
				except Exception as e:
					self.logger.logWarn(str(e), flush=True)
					self.logger.log("Wait 5 seconds and try again.", flush=True)
					self.status.addOneTimeNotificationError("Error while connecting Arduino. Retry in 5 seconds.")
					time.sleep(5)

		self.connecting = False
		self.connected = True
		self.logger.log("Arduino connected", flush=True)
		self.status.addOneTimeNotificationSuccess("Arduino connected")

		return True

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

	def isConnected(self):
		return self.serial != None

	def sendPing(self):
		# TODO: Ping ausarbeiten
		# self.serial.write('p\n')
		self.logger.logWarn("Arduino: Ping not implemented!")
		return False

	def sendInit(self): #TODO: Object mit allen Tubes und ihre Pins als Übergabeparameter
		# TODO: Init ausarbeiten
		# self.serial.write('i\n')
		self.logger.logWarn("Arduino: Init not implemented!")
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
			if self.serial.write((msg + '\n').encode()):
				self.logger.log("Message sent to Arduino: " + msg)
			else:
				self.logger.logErr("Sending message to Arduino failed")
			return True
