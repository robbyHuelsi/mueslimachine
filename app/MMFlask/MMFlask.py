from flask import Flask, session, render_template, request, jsonify, redirect, url_for
from flask.views import View, MethodView
import json

from MMFlask.MMFlaskNav import MMFlaskNav


class MMFlask(Flask):
    def __init__(self, muesli_machine):
        super().__init__(__name__)

        self.mm = muesli_machine

        self.static_folder = "../static"
        self.template_folder = "../templates"

        self.nav = MMFlaskNav(self)

        self.register_urls_default("index")
        self.register_urls_default("status")
        self.register_urls_default("signup")
        self.register_urls_default("login")
        self.register_urls_default("logout")

        # self.register_urls_default("led")
        # self.register_urls_default("scale")

        self.register_urls_for_items("user")
        self.register_urls_for_items("tube")
        self.register_urls_for_items("ingredient")
        self.register_urls_for_items("recipe")

        self.add_url_rule('/ajaxStatus', methods=['POST'],
                          view_func=MMFlaskViewAjaxStatus.as_view('flaskAjaxStatus', muesli_machine=self.mm))
        self.add_url_rule('/ajaxSignUp', methods=['POST'],
                          view_func=MMFlaskViewAjaxSignUp.as_view('flaskAjaxSignUp', muesli_machine=self.mm))

        # TODO: Keep this really secret:
        self.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

    def register_urls_default(self, name):
        url = "/" + name + "/" if name != "index" else "/"
        view_func = MMFlaskViewDefaultRenderer.as_view(name, endpoint_name=name, muesli_machine=self.mm)
        self.add_url_rule(url, view_func=view_func)

    def register_urls_for_items(self, name):
        url = "/" + name + "/"
        method_view = MMFlaskViewForItemsRenderer(endpoint_name=name, muesli_machine=self.mm)
        view_func_list, view_func_single, view_func_add = method_view.as_view()
        self.add_url_rule(url, view_func=view_func_list, methods=['GET', ], defaults={"item_id": None})
        self.add_url_rule(url + "<int:item_id>/", view_func=view_func_single, methods=['GET', ])
        self.add_url_rule(url + "<int:item_id>/", view_func=view_func_single, methods=['POST', ])
        self.add_url_rule(url + "add/", view_func=view_func_add, methods=['GET', ], defaults={"item_id": "add"})
        self.add_url_rule(url + "add/", view_func=view_func_add, methods=['POST', ], defaults={"item_id": "add"})


class MMFlaskViewDefaultRenderer(MethodView):
    def __init__(self, endpoint_name, muesli_machine):
        self.endpoint_name = endpoint_name
        self.templateName = endpoint_name + ".html"
        self.mm = muesli_machine
        super().__init__()

    def get(self):
        if self.endpoint_name == "logout":
            return self.logout()
        elif self.endpoint_name == "status":
            return render_template(self.templateName, status=self.mm.status.get_status())
        else:
            return render_template(self.templateName)

    def post(self):
        if self.endpoint_name == "login":
            return self.login()

        elif self.endpoint_name == "logout":
            return self.logout()

        else:
            return ""

    def login(self):
        in_username = request.form['inputUsername']
        in_password = request.form['inputPassword']

        if in_username and in_password:
            if self.mm.mySQL.user_check_user_password(in_username, in_password):
                session['username'] = in_username
                return redirect(url_for('index'))

        return redirect(url_for('login'))

    def logout(self):
        if 'username' in session:
            session.pop('username', None)
        return redirect(url_for('index'))


class MMFlaskViewForItemsRenderer(MethodView):
    def __init__(self, endpoint_name, muesli_machine):
        self.endpoint_name = endpoint_name
        self.mm = muesli_machine
        super().__init__()

    def as_view(self):
        view_list = super().as_view(self.endpoint_name, endpoint_name=self.endpoint_name, muesli_machine=self.mm)
        view_single = super().as_view(self.endpoint_name + "Single", endpoint_name=self.endpoint_name,
                                      muesli_machine=self.mm)
        view_add = super().as_view(self.endpoint_name + "Add", endpoint_name=self.endpoint_name, muesli_machine=self.mm)
        return view_list, view_single, view_add

    def get(self, item_id):
        if item_id is None:
            # self.mm.logger.log("Show List of " + self.endpoint_name)
            items = self.mm.mySQL.get_items(self.endpoint_name)
            return render_template(self.endpoint_name + "List.html", items=items)
        elif item_id == "add":
            return render_template(self.endpoint_name + "Single.html", item=None)
        else:
            # self.mm.logger.log("Show Single View of " + self.endpoint_name + "Id " + str(item_id))
            item = self.mm.mySQL.get_item_by_id(self.endpoint_name, item_id)
            if len(item) == 1:
                return render_template(self.endpoint_name + "Single.html", item=item)
            else:
                # If number of MySQL response items are 0 or > 1:
                return redirect(url_for(self.endpoint_name))

    def post(self, item_id):
        cmd = request.form.get("cmd")
        success = False

        # Add new item to items list
        if cmd == "add":
            self.mm.logger.log("Adding " + self.endpoint_name + "...")

            # Get properties of new item from page
            if self.endpoint_name == "user":
                in_first_name = request.form.get("inputFirstName")
                in_last_name = request.form.get("inputLastName")
                in_username = request.form.get("inputUsername")
                in_email = request.form.get("inputEmail")
                in_password = request.form.get("inputPassword")
                in_role = "admin"
                properties = (in_username, in_first_name, in_last_name, in_password, in_email, in_role)
            elif self.endpoint_name == "tube":
                properties = (request.form.get("pin1"), request.form.get("pin2"),
                              request.form.get("pin3"), request.form.get("pin4"))
            else:
                properties = ()

            self.mm.logger.log("Properties: " + str(properties))
            self.mm.logger.log("Count of prop.: " + str(len(properties)))

            # If properties are available, add new item
            if len(properties) > 0:
                success, item_id = self.mm.mySQL.add_item(self.endpoint_name, properties)

            # If adding new item was successful go to its single page or if not go to list page
            if success:
                self.mm.logger.log("item_id : " + str(item_id))
                return redirect(url_for(self.endpoint_name) + str(item_id) + "/")
            else:
                self.mm.status.add_one_time_notification_error("Adding " + self.endpoint_name.title() + " failed.")
                return redirect(url_for(self.endpoint_name))

        elif cmd == "edit":
            if item_id is not None:
                self.mm.logger.log("Editing " + self.endpoint_name + " #" + str(item_id) + "...")
                success = self.mm.mySQL.edit_item_by_id(self.endpoint_name, item_id, request.form)
            if success:
                self.mm.status.add_one_time_notification_success(
                    self.endpoint_name.title() + " #" + str(item_id) + " edited successfully.")
            else:
                self.mm.status.add_one_time_notification_error(
                    "Editing " + self.endpoint_name.title() + " #" + str(item_id) + " failed.")
            return redirect(url_for(self.endpoint_name) + str(item_id) + "/")

        elif cmd == "delete":
            if item_id is not None:
                # self.mm.logger.log("Deleting " + self.endpoint_name + " #" + str(item_id) + "...")
                success = self.mm.mySQL.delete_item_by_id(self.endpoint_name, item_id)
            if success:
                self.mm.status.add_one_time_notification_success(
                    self.endpoint_name.title() + " #" + str(item_id) + " deleted successfully.")
            else:
                self.mm.status.add_one_time_notification_error(
                    "Deleting " + self.endpoint_name.title() + " #" + str(item_id) + " failed.")
            return redirect(url_for(self.endpoint_name))


class MMFlaskViewAjaxStatus(View):
    def __init__(self, muesli_machine):
        self.mm = muesli_machine
        super().__init__()

    def dispatch_request(self):
        cmd = request.form.get("cmd")
        request_id = request.form.get("request_id")
        self.mm.logger.log("Request ID: " + str(request_id))

        if cmd and cmd != "":
            self.mm.logger.log(cmd)

            # Example:
            # {
            #    "stepper":{
            #       "id": 0,
            #       "steps": 300
            #    }
            # }

            parsed = False

            try:
                cmd = json.loads(cmd)
                parsed = True
            except Exception as e:
                self.mm.logger.log_error("cmd is not in JSON format. Err Msg: {}".format(e))

            if parsed:
                if "stepper" in cmd:
                    stepper_id = cmd["stepper"]["id"]
                    steps = cmd["stepper"]["steps"]
                    self.mm.logger.log("Stepper ID " + str(stepper_id))
                    self.mm.logger.log("Steps " + str(steps))
                    self.mm.arduino.send_drive(stepper_id, steps)
            # elif cmd == 'ledRedOn':
            # 	self.mm.ledRed.on()
            # elif cmd == 'ledRedOff':
            # 	self.mm.ledRed.off()
            # elif cmd == 'ledYellowOn':
            # 	self.mm.ledYellow.on()
            # elif cmd == 'ledYellowOff':
            # 	self.mm.ledYellow.off()
            # elif cmd == 'servo1On':
            # 	self.mm.servo1.on()
            # elif cmd == 'servo1Off':
            # 	self.mm.servo1.off()
            # elif cmd == 'tare':
            # 	self.mm.scale.tare()

        # self.mm.logger.log(scale.getAverage())
        return jsonify(self.mm.status.get_status(request_id))


class MMFlaskViewAjaxSignUp(View):
    def __init__(self, muesli_machine):
        self.mm = muesli_machine
        super().__init__()

    def dispatch_request(self):
        in_first_name = request.form.get("inputFirstName")
        in_last_name = request.form.get("inputLastName")
        in_username = request.form.get("inputUsername")
        in_email = request.form.get("inputEmail")
        in_password = request.form.get("inputPassword")
        in_role = "admin"

        if in_username and in_email and in_password:
            msg = self.mm.mySQL.user_create_user(in_username, in_first_name, in_last_name,
                                                 in_password, in_email, in_role)
            self.mm.logger.log(msg)
        else:
            self.mm.status.add_one_time_notification_warning("Enter all required fields")

        return jsonify(self.mm.status.get_status())
