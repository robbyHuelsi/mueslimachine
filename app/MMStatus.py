class MMStatus:
    def __init__(self):
        self.json = {}
        self.databaseStatus = 0
        self.arduinoStatus = 0
        self.gpios_in = []
        self.gpios_out = []
        self.oneTimeNotification = []

    def get_status(self, request_id=None):
        if request_id:
            self.json["request_id"] = request_id

        if self.oneTimeNotification:
            self.json["notification"] = self.oneTimeNotification
            del self.oneTimeNotification
            self.oneTimeNotification = []

        self.json["database"] = self.databaseStatus
        self.json["arduino"] = self.arduinoStatus

        self.json["gpio_in"] = []
        for gpio_in in self.gpios_in:
            gpio_in_json_data = [{"type": gpio_in.__class__.__name__,
                                  "name": gpio_in.getName(), "value": gpio_in.getValue()}]
            self.json["gpio_in"] += gpio_in_json_data

        self.json["gpio_out"] = []
        for gpio_out in self.gpios_out:
            self.json["gpio_out"] += [
                {"type": gpio_out.__class__.__name__, "name": gpio_out.getName(), "value": gpio_out.getValue()}]

        json_to_send = self.json
        del self.json
        self.json = {}
        return json_to_send

    def set_database_status(self, database_status):
        self.databaseStatus = database_status
        return True

    def set_arduino_status(self, arduino_status):
        self.arduinoStatus = arduino_status
        return True

    def register_gpio_in(self, gpio_in):
        self.gpios_in.append(gpio_in)

    def register_gpio_out(self, gpio_out):
        self.gpios_out.append(gpio_out)

    def add_one_time_notification(self, msg):
        self.oneTimeNotification += [{"type": "alert-dark", "msg": msg}]

    def add_one_time_notification_success(self, msg):
        self.oneTimeNotification += [{"type": "alert-success", "msg": msg}]

    def add_one_time_notification_warning(self, msg):
        self.oneTimeNotification += [{"type": "alert-warning", "msg": msg}]

    def add_one_time_notification_error(self, msg):
        self.oneTimeNotification += [{"type": "alert-danger", "msg": msg}]
