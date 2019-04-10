import json
# Auskommentiert wg. Docker-Test
# from mmGpio import mmGpioInHx711

class mmStatus():
	def __init__(self):
		self.json = {}
		self.databaseStatus = 0
		self.arduinoStatus = 0
		self.gpiosIn = []
		self.gpiosOut = []
		self.oneTimeNotification = []
		
	def getStatus(self, requestId = None):
		if requestId:
			self.json["requestId"] = requestId

		if self.oneTimeNotification:
			self.json["notification"] = self.oneTimeNotification
			del self.oneTimeNotification
			self.oneTimeNotification = []

		self.json["database"] = self.databaseStatus
		self.json["arduino"] = self.arduinoStatus
		
		self.json["gpioin"] = []
		for gpioIn in self.gpiosIn:
			gpioInJsonData = [{"type":gpioIn.__class__.__name__, "name":gpioIn.getName(), "value":gpioIn.getValue()}]
			# Auskommentiert wg. Docker-Test
			# if(isinstance(gpioIn, mmGpioInHx711)):
			# 	gpioInJsonData[0]['offset'] = gpioIn.getOffset()
			# 	gpioInJsonData[0]['refUnit'] = gpioIn.getRefUnit()
			self.json["gpioin"] += gpioInJsonData
		
		self.json["gpioout"] = []
		for gpioOut in self.gpiosOut:
			self.json["gpioout"] += [{"type":gpioOut.__class__.__name__, "name":gpioOut.getName(), "value":gpioOut.getValue()}]
			
		jsonToSend = self.json
		del self.json
		self.json = {}
		return jsonToSend
	
	def setDatabaseStatus(self,databaseStatus):
		self.databaseStatus = databaseStatus
		return True

	def setArduinoStatus(self,arduinoStatus):
		self.arduinoStatus = arduinoStatus
		return True

	def registerGpioIn(self, gpioIn):
		self.gpiosIn.append(gpioIn)
		
	def registerGpioOut(self, gpioOut):
		self.gpiosOut.append(gpioOut)
		
	def addOneTimeNotification(self, msg):
		self.oneTimeNotification += [{"type":"alert-dark", "msg":msg}]
		
	def addOneTimeNotificationSuccess(self, msg):
		self.oneTimeNotification += [{"type":"alert-success", "msg":msg}]
		
	def addOneTimeNotificationWarning(self, msg):
		self.oneTimeNotification += [{"type":"alert-warning", "msg":msg}]
		
	def addOneTimeNotificationError(self, msg):
		self.oneTimeNotification += [{"type":"alert-danger", "msg":msg}]