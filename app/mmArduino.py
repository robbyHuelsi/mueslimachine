from serial import Serial
import threading
import time

class mmArduino():
	
	def __init__(self, logger, mmStatus, port):
		self.logger = logger
		self.mmStatus = mmStatus
		self.port = port
		
		self.setStatus(0) # 0 => disconnected / 1 => connecting / 2 => setting up / 3 => connected
		self.serial = None
		self.time = None

		connectingThread = threading.Thread(target=self.connect, args=())
		connectingThread.daemon = True 
		connectingThread.start()
	   
	def __del__(self):
		if self.status == 2 or self.status == 3:
			self.serial.close()
			self.logger.log("Arduino connection closed")

	def connect(self):
		if self.status == 1:
			self.logger.logErr("Another thread is trying to connect to Arduino")
			return False
		elif self.status == 2 or self.status == 3:
			self.logger.logErr("Aduino is already connected")
			return False
		elif self.status == 0:
			self.setStatus(1)
			# In case Arduino is not up yet try to connect every 5 seconds
			while True:
				try:
					self.serial = Serial(self.port, 300)
					self.setStatus(2)
					# TODO: self.sendPing() ...
					break
				except Exception as e:
					self.logger.logWarn(str(e), flush=True)
					self.logger.log("Wait 5 seconds and try again.", flush=True)
					time.sleep(5)
			self.setStatus(3)
			self.logger.log("Arduino connected", flush=True)
			return True
		else:
			self.logger.logErr("Something went wrong while connecting Arduino")
			return False

	def close(self):
		if self.status == 2 or self.status == 3:
			try:
				self.serial.close()
			except Exception as e:
				self.logger.logErr(str(e))
				return False
		self.serial = None
		self.time = None
		self.hasSetup = False
		return True

	def setStatus(self, status):
		# 0 => disconnected / 1 => connecting / 2 => setting up / 3 => connected
		self.status = status
		self.mmStatus.setArduinoStatus(status)
		return True

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
