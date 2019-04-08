import RPi.GPIO as GPIO
from hx711 import HX711

class mmGpio():
	count = 0
	
	def __init__(self, pin, name):
		self.pin = pin
		self.name = name
		self.value = 0
		self.id = mmGpio.count
		GPIO.setmode(GPIO.BCM)
		mmGpio.count += 1
		print("GPIO added (Name: " + self.name + "; Pin: " + str(self.pin) + "; No.: " + str(self.id) + ")")
	   
	def __del__(self):
		mmGpio.count -= 1
		print("GPIO deleted (Name: " + self.name + "; Pin: " + str(self.pin) + "; No.: " + str(self.id) + ")")
		if mmGpio.count <= 0:
			try:
				GPIO.cleanup()
				print("GPIO cleaned up")
			except:
				pass
		
	def getName(self):
		return self.name
	
	def getValue(self):
		return self.value


class mmGpioIn(mmGpio):
	def __init__(self, pin, name, mmStatus):
		mmGpio.__init__(self, pin, name)
		mmStatus.registerGpioIn(self)
		GPIO.setup(self.pin, GPIO.IN)

class mmGpioOut(mmGpio):
	def __init__(self, pin, name, mmStatus):
		mmGpio.__init__(self, pin, name)
		mmStatus.registerGpioOut(self)
		GPIO.setup(self.pin, GPIO.OUT)

class mmGpioOutBinary(mmGpioOut):
	def __init__(self, pin, potentialForOff, name, mmStatus):
		mmGpioOut.__init__(self, pin, name, mmStatus)
		self.potentialForOff = potentialForOff
		GPIO.output(self.pin, self.potentialForOff)
		
	def off(self):
		GPIO.output(self.pin, self.potentialForOff)
		self.value = 0
		
	def on(self):
		if(self.potentialForOff == 0):
			GPIO.output(self.pin, GPIO.HIGH)
		else:
			GPIO.output(self.pin, GPIO.LOW)
		self.value = 1
		
	def toggle(self):
		if(self.value == 0):
			self.on()
		else:
			self.off()
			
			
class mmGpioInHx711(mmGpioIn):
	def __init__(self, pin1, pin2, name, refUnit, mmStatus):
		mmGpioIn.__init__(self, pin1, name, mmStatus)
		self.hx = HX711(pin1, pin2)
		self.hx.set_reading_format("LSB", "MSB")
		self.hx.set_reference_unit(refUnit)
		self.hx.reset()
		self.hx.tare()
		
		self.sum = 0
		self.count = 0
		
	def getValue(self):
		self.value = self.hx.get_weight(5)
		self.hx.power_down()
		self.hx.power_up()
		self.sum += self.value
		self.count += 1
		return int(self.value)
	
	#def getWeight(self):
	#    weight = self.hx.get_weight(5)
	#    self.hx.power_down()
	#    self.hx.power_up()
	#    return weight
	   
	def getOffset(self):
		return self.hx.get_offset()
		
	def getRefUnit(self):
		return self.hx.get_reference_unit()
	
	def getAverage(self):
		if self.count > 0:
			return int(self.sum / self.count)
		else:
			return 0
	
	def setOffset(self, offset):
		self.hx.set_offset(offset)
		self.sum = 0
		self.count = 0

	def setRefUnit(self, refUnit):
		self.hx.set_reference_unit(refUnit)
		self.sum = 0
		self.count = 0
		
	def tare(self):
		self.hx.tare()
		self.sum = 0
		self.count = 0


