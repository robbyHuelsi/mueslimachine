#!/usr/bin/python
#
import os
from MMLogger import MMLogger
from MMFlask.MMFlask import MMFlask
from MMStatus import MMStatus
from MMMySql import MMMySql
from MMArduino import MMArduino
# from MMGpio import *
# from MMGpioServo import *


class MuesliMachine:
    def __init__(self):
        db_host = os.getenv("DB_HOST", "127.0.0.1")
        db_port = int(os.getenv("DB_PORT", 3306))
        db_user = os.getenv("DB_USER", "root")
        db_pass = os.getenv("DB_PASS", "root")
        db_name = os.getenv("DB_NAME", "muesli_machine")
        arduino_port = os.getenv("ARDUINO_PORT", "/dev/ttyUSB0")

        self.logger = MMLogger()

        self.flask = MMFlask(self)

        self.status = MMStatus()
        self.mySQL = MMMySql(self.logger, self.flask, self.status, db_user, db_pass, db_host, db_port, db_name)

        self.arduino = MMArduino(self.logger, self.status, arduino_port)

        # self.ledRed = MMGpioOutBinary(4,0,"LED Red", self.status)
        # self.ledYellow = MMGpioOutBinary(17,0,"LED Yellow", self.status)
        # self.servo1 = MMGpioServo(22, "Servo 1", self.status)

        # ref_unit = -1026300 / 503
        # self.scale = MMGpioInHx711(5, 6, "Scale", ref_unit, self.status) #(self, pin1, pin2, name, ref_unit, MMStatus)

        self.flask.run(debug=True, host='0.0.0.0', port=80)


if __name__ == '__main__':
    MuesliMachine()
