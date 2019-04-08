import serial
from datetime import datetime

class mmArduino():
	
	def __init__(self, port, status):
		self.status = status
		# TODO: self.serial = serial.Serial(port, 300)
		self.time = datetime.now()
		self.hasSetup = True #TODO: False
	   
	def __del__(self):
		# TODO: self.serial.close()
		pass

	def sendInit(self): #TODO: Object mit allen Tubes und ihre Pins als Übergabeparameter
		# TODO: Init ausarbeiten
		# self.serial.write('i\n')
		print("Init not implemented!")

	def sendDrive(self, id, steps) :
		if self.hasSetup:
			# TODO: self.serial.write('d,' + str(id) + ',' + str(steps) + '\n')
			pass
		else:
			pass # TODO: Hinweis, auf notwendige Initialisierung
