import RPi.GPIO as GPIO
import threading
import time

from MMGpio import MMGpioOut


class MMGpioServo(MMGpioOut):
    t = None
    
    def __init__(self, pin, name, mmStatus):
        MMGpioOut.__init__(self, pin, name, mmStatus)
        self.t = threading.Thread(target=self.__doit, args=(pin,)) 

    def __del__(self):
        self.off()
        MMGpioOut.__del__(self)
        
    def on(self):
        self.t.start()
        
    def off(self):
        if not self.t == None:
            self.t.doRun = False

    def __doit(self, pin):
        t = threading.currentThread()
        p = GPIO.PWM(pin, 50) # PWM mit 50Hz
        p.start(0) # Initialisierung
        while getattr(t, "doRun", True):
            for i in range(50):
                p.ChangeDutyCycle(i)
                time.sleep(0.5)
        print("Thread stopped")