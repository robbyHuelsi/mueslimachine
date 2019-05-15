from serial import Serial
import threading
import time


class MMArduino:
    def __init__(self, logger, mm_status, port):
        self.logger = logger
        self.mm_status = mm_status
        self.port = port

        self.status = 0
        self.has_setup = False

        self.set_status(0)  # 0 => disconnected / 1 => connecting / 2 => setting up / 3 => connected
        self.serial = None
        self.time = None

        connecting_thread = threading.Thread(target=self.connect, args=())
        connecting_thread.daemon = True
        connecting_thread.start()

    def __del__(self):
        if self.status == 2 or self.status == 3:
            self.serial.close()
            self.logger.log("Arduino connection closed")

    def connect(self):
        if self.status == 1:
            self.logger.log_error("Another thread is trying to connect to Arduino")
            return False
        elif self.status == 2 or self.status == 3:
            self.logger.log_error("Aduino is already connected")
            return False
        elif self.status == 0:
            self.set_status(1)
            # In case Arduino is not up yet try to connect every 5 seconds
            while True:
                try:
                    self.serial = Serial(self.port, 300)
                    self.set_status(2)
                    # TODO: self.send_ping() ...
                    break
                except Exception as e:
                    self.logger.log_warn(str(e), flush=True)
                    self.logger.log("Wait 5 seconds and try again.", flush=True)
                    time.sleep(5)
            self.set_status(3)
            self.logger.log("Arduino connected", flush=True)
            return True
        else:
            self.logger.log_error("Something went wrong while connecting Arduino")
            return False

    def close(self):
        if self.status == 2 or self.status == 3:
            try:
                self.serial.close()
            except Exception as e:
                self.logger.log_error(str(e))
                return False
        self.serial = None
        self.time = None
        self.has_setup = False
        return True

    def set_status(self, status):
        # 0 => disconnected / 1 => connecting / 2 => setting up / 3 => connected
        self.status = status
        self.mm_status.set_arduino_status(status)
        return True

    def send_ping(self):
        # TODO: Ping ausarbeiten
        # self.serial.write('p\n')
        self.logger.log_warn("Arduino: Ping not implemented!")
        return False

    def send_init(self):  # TODO: Object mit allen Tubes und ihre Pins als Übergabeparameter
        # TODO: Init ausarbeiten
        # self.serial.write('i\n')
        self.logger.log_warn("Arduino: Init not implemented!")
        return False

    def send_drive(self, tube_id, steps):
        if self.serial is None:
            self.logger.log_error("Serial Port not open")
            return False
        elif self.has_setup is False:
            self.logger.log_error("Serial Port not set up")
            return False
        else:
            msg = 'd,' + str(tube_id) + ',' + str(steps)
            if self.serial.write((msg + '\n').encode()):
                self.logger.log("Message sent to Arduino: " + msg)
            else:
                self.logger.log_error("Sending message to Arduino failed")
            return True
