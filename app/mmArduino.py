from serial import Serial
from datetime import datetime

class mmArduino():
	
	def __init__(self, port, status):
		self.serial = None
		self.port = port
		self.status = status
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
			print(e)
			return False
		self.time = datetime.now()
		self.hasSetup = True #TODO: False

	def close(self):
		if self.serial != None:
			try:
				self.serial.close()
			except Exception as e:
				print(e)
				return False
		self.serial = None
		self.time = None
		self.hasSetup = False
		return True

	def sendInit(self): #TODO: Object mit allen Tubes und ihre Pins als Übergabeparameter
		# TODO: Init ausarbeiten
		# self.serial.write('i\n')
		print("Init not implemented!")
		return False

	def sendDrive(self, id, steps) :
		if self.serial == None:
			# TODO: Hinweis, dass nicht offen
			return False
		elif self.hasSetup == False:
			# TODO: Hinweis auf notwendige Initialisierung
			return False
		else:
			self.serial.write('d,' + str(id) + ',' + str(steps) + '\n')
			return True
