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

        self.sites = [{'url': 'index',
                       'name': 'Index',
                       'nav': {'top': False},
                       'reg_func': self.register_urls_default,
                       'permission': {'anonymous': False,
                                      'pending': False,
                                      'user': True,
                                      'admin': True}},
                      {'url': 'startup',
                       'name': 'Start Up',
                       'nav': {'top': False},
                       'reg_func': self.register_urls_default,
                       'permission': {'anonymous': True,
                                      'pending': True,
                                      'user': True,
                                      'admin': True}},
                      {'url': 'welcome',
                       'name': 'Welcome',
                       'nav': {'top': False},
                       'reg_func': self.register_urls_default,
                       'permission': {'anonymous': True,
                                      'pending': False,
                                      'user': False,
                                      'admin': False}},
                      {'url': 'recipe',
                       'name': 'Recipes',
                       'nav': {'top': True},
                       'reg_func': self.register_urls_for_items,
                       'permission': {'anonymous': False,
                                      'pending': False,
                                      'user': True,
                                      'admin': True}},
                      {'url': 'ingredient',
                       'name': 'Ingredients',
                       'nav': {'top': True},
                       'reg_func': self.register_urls_for_items,
                       'permission': {'anonymous': False,
                                      'pending': False,
                                      'user': False,
                                      'admin': True}},
                      {'url': 'tube',
                       'name': 'Tubes',
                       'nav': {'top': True},
                       'reg_func': self.register_urls_for_items,
                       'permission': {'anonymous': False,
                                      'pending': False,
                                      'user': False,
                                      'admin': True}},
                      {'url': 'user',
                       'name': 'Users',
                       'nav': {'top': True},
                       'reg_func': self.register_urls_for_items,
                       'permission': {'anonymous': False,
                                      'pending': False,
                                      'user': False,
                                      'admin': True}},
                      {'url': 'led',
                       'name': 'LED',
                       'nav': {'top': True},
                       'reg_func': self.register_urls_default,
                       'permission': {'anonymous': False,
                                      'pending': False,
                                      'user': False,
                                      'admin': True}},
                      {'url': 'scale',
                       'name': 'Scale',
                       'nav': {'top': True},
                       'reg_func': self.register_urls_default,
                       'permission': {'anonymous': False,
                                      'pending': False,
                                      'user': False,
                                      'admin': True}},
                      {'url': 'status',
                       'name': 'Status',
                       'nav': {'top': True},
                       'reg_func': self.register_urls_default,
                       'permission': {'anonymous': False,
                                      'pending': False,
                                      'user': False,
                                      'admin': True}},
                      {'url': 'signup',
                       'name': 'Sign Up',
                       'nav': {'top': False},
                       'reg_func': self.register_urls_default,
                       'permission': {'anonymous': True,
                                      'pending': False,
                                      'user': False,
                                      'admin': False}},
                      {'url': 'login',
                       'name': 'Log In',
                       'nav': {'top': True},
                       'reg_func': self.register_urls_default,
                       'permission': {'anonymous': True,
                                      'pending': False,
                                      'user': False,
                                      'admin': False}},
                      {'url': 'logout',
                       'name': 'Log Out',
                       'nav': {'top': True},
                       'reg_func': self.register_urls_default,
                       'permission': {'anonymous': False,
                                      'pending': True,
                                      'user': True,
                                      'admin': True}},
                      ]

        self.redirections = {'anonymous': 'login',
                             'pending': 'login',
                             'user': 'index',
                             'admin': 'index'}

        self.nav = MMFlaskNav(self)

        for site in self.sites:
            site['reg_func'](site['url'])

        self.add_url_rule('/ajaxStatus', methods=['POST'],
                          view_func=MMFlaskViewAjaxStatus.as_view('flaskAjaxStatus', muesli_machine=self.mm))

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

    def check_get_permission(self, endpoint_name, user_role):
        db_not_ready = self.mm.status.get_status()['database'] != 3
        if db_not_ready and endpoint_name != 'startup':
            return False, 'startup'
        elif not db_not_ready and endpoint_name == 'startup':
            return False, self.redirections[user_role]

        is_setup_mode = self.mm.mySQL.setting_is_setup_mode()
        if is_setup_mode and endpoint_name != 'welcome':
            return False, 'welcome'
        elif not is_setup_mode and endpoint_name == 'welcome':
            return False, self.redirections[user_role]

        for site in self.sites:
            if site['url'] == endpoint_name:
                if not site['permission'][user_role]:
                    return False, self.redirections[user_role]

        return True, ''

    def get_user_by_id(self, session):
        self.mm.logger.log(str(session))
        if 'user_uid' in session:
            user = self.mm.mySQL.get_item_by_id(self.mm.mySQL.get_tbl_names().TBL_USER, session['user_uid'])
            if len(user) > 0:
                current_user = {'user_uid': user[0]['user_uid'],
                                'user_username': user[0]['user_username'],
                                'user_first_name': user[0]['user_first_name'],
                                'user_last_name': user[0]['user_last_name'],
                                'user_email': user[0]['user_email'],
                                'user_role': user[0]['user_role']}
                return current_user
            else:
                del session['user_uid']
        current_user = {'user_uid': -1,
                        'user_role': 'anonymous'}
        return current_user


class MMFlaskViewDefaultRenderer(MethodView):
    def __init__(self, endpoint_name, muesli_machine):
        self.endpoint_name = endpoint_name
        self.templateName = endpoint_name + ".html"
        self.mm = muesli_machine
        super().__init__()

    def get(self):
        mm_current_user = self.mm.flask.get_user_by_id(session)
        allowed, redirect_url = self.mm.flask.check_get_permission(self.endpoint_name, mm_current_user['user_role'])
        if not allowed:
            return redirect(url_for(redirect_url))

        if self.endpoint_name == "logout":
            return self.logout()
        elif self.endpoint_name == "status":
            return render_template(self.templateName,
                                   mm_current_user=mm_current_user,
                                   mm_status=self.mm.status.get_status(),
                                   mm_version=self.mm.version)
        else:
            return render_template(self.templateName,
                                   mm_current_user=mm_current_user,
                                   mm_status=self.mm.status.get_status(),
                                   mm_version=self.mm.version)

    def post(self):
        if self.endpoint_name == "welcome":
            return self.setup_or_signup(True)

        if self.endpoint_name == "signup":
            return self.setup_or_signup(False)

        if self.endpoint_name == "login":
            return self.login()

        elif self.endpoint_name == "logout":
            return self.logout()

        else:
            return ""

    def setup_or_signup(self, is_setup):
        in_first_name = request.form.get("first_name")
        in_last_name = request.form.get("last_name")
        in_username = request.form.get("username")
        in_email = request.form.get("email")
        in_password = request.form.get("password")
        in_password_confirm = request.form.get("password_confirm")
        in_role = "admin" if is_setup else 'pending'

        success = True
        err_msg = ''

        if in_password != in_password_confirm:
            success = False
            err_msg = "Confirmed password was different"

        if success:
            tbl = self.mm.mySQL.get_tbl_names().TBL_USER
            properties = (in_username, in_first_name,
                          in_last_name, in_password,
                          in_email, in_role)
            success, item, err_msg = self.mm.mySQL.add_item(tbl, properties)
            # TODO: Rewrite error messages

        if success and is_setup:
            self.mm.mySQL.setting_update_value_by_key('setup_mode', 'false')
            return redirect(url_for('index'))
        elif success:
            return redirect(url_for('index'))
        else:
            self.mm.status.add_one_time_notification_error(err_msg)
            user = {'user_username': in_username,
                    'user_first_name': in_first_name,
                    'user_last_name': in_last_name,
                    'user_email': in_email}
            return render_template(self.templateName, user=user, mm_version=self.mm.version)

    def login(self):
        in_username = request.form['username']
        in_password = request.form['password']

        if in_username and in_password:
            password_okay, user_uid = self.mm.mySQL.user_check_user_password(in_username, in_password)
            if password_okay:
                session['user_uid'] = user_uid
                return redirect(url_for('index'))
            else:
                self.mm.status.add_one_time_notification_error("Login failed!")

        return redirect(url_for('login'))

    @staticmethod
    def logout():
        if 'user_uid' in session:
            del session['user_uid']
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

    def render_template_list(self, items, mm_current_user):
        self.mm.logger.log(str(items))
        if self.endpoint_name == self.mm.mySQL.get_tbl_names().TBL_INGREDIENT:
            tubes = self.mm.mySQL.get_items(self.mm.mySQL.get_tbl_names().TBL_TUBE)
            return render_template(self.endpoint_name + "List.html",
                                   mm_current_user=mm_current_user,
                                   mm_version=self.mm.version,
                                   ingredients=items, tubes=tubes)
        elif self.endpoint_name == self.mm.mySQL.get_tbl_names().TBL_RECIPE:
            ingredients = self.mm.mySQL.get_items(self.mm.mySQL.get_tbl_names().TBL_TUBE)
            return render_template(self.endpoint_name + "List.html",
                                   mm_current_user=mm_current_user,
                                   mm_version=self.mm.version,
                                   recipes=items, ingredients=ingredients)
        else:
            return render_template(self.endpoint_name + "List.html",
                                   mm_current_user=mm_current_user,
                                   mm_version=self.mm.version,
                                   items=items)

    def render_template_single(self, item, mm_current_user):
        self.mm.logger.log(str(item))
        if self.endpoint_name == self.mm.mySQL.get_tbl_names().TBL_INGREDIENT:
            tubes = self.mm.mySQL.get_items(self.mm.mySQL.get_tbl_names().TBL_TUBE)
            return render_template(self.endpoint_name + "Single.html",
                                   mm_current_user=mm_current_user,
                                   mm_version=self.mm.version,
                                   ingredient=item, tubes=tubes)
        elif self.endpoint_name == self.mm.mySQL.get_tbl_names().TBL_RECIPE:
            all_ingredients = self.mm.mySQL.get_items(self.mm.mySQL.get_tbl_names().TBL_INGREDIENT)
            self.mm.logger.log("ir_get_ingredients_by_recipe_id: " + str(item))
            if item is None:
                used_ingredients = []
            else:
                used_ingredients = self.mm.mySQL.ir_get_ingredients_by_recipe_id(item[0])
            return render_template(self.endpoint_name + "Single.html",
                                   mm_current_user=mm_current_user,
                                   mm_version=self.mm.version,
                                   recipes=item, all_ingredients=all_ingredients, used_ingredients=used_ingredients)
        else:
            return render_template(self.endpoint_name + "Single.html",
                                   mm_current_user=mm_current_user,
                                   mm_version=self.mm.version,
                                   item=item)

    def get(self, item_id):
        mm_current_user = self.mm.flask.get_user_by_id(session)
        allowed, redirect_url = self.mm.flask.check_get_permission(self.endpoint_name, mm_current_user['user_role'])
        if not allowed:
            return redirect(url_for(redirect_url))

        if item_id is None:
            # self.mm.logger.log("Show List of " + self.endpoint_name)
            items = self.mm.mySQL.get_items(self.endpoint_name)
            return self.render_template_list(items=items, mm_current_user=mm_current_user)
        elif item_id == "add":
            return self.render_template_single(item=None, mm_current_user=mm_current_user)
        else:
            # self.mm.logger.log("Show Single View of " + self.endpoint_name + "Id " + str(item_id))
            item = self.mm.mySQL.get_item_by_id(self.endpoint_name, item_id)
            if len(item) == 1:
                return self.render_template_single(item=item, mm_current_user=mm_current_user)
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
            if self.endpoint_name == self.mm.mySQL.get_tbl_names().TBL_USER:
                in_first_name = request.form.get("first_name")
                in_last_name = request.form.get("last_name")
                in_username = request.form.get("username")
                in_email = request.form.get("email")
                in_password = request.form.get("password")
                in_password_confirm = request.form.get("password_confirm")
                in_role = "admin"
                properties = (in_username, in_first_name, in_last_name, in_password, in_email, in_role)
            elif self.endpoint_name == self.mm.mySQL.get_tbl_names().TBL_TUBE:
                properties = (request.form.get("pin_1"), request.form.get("pin_2"),
                              request.form.get("pin_3"), request.form.get("pin_4"))
            elif self.endpoint_name == self.mm.mySQL.get_tbl_names().TBL_INGREDIENT:
                in_name = request.form.get("name")
                in_price = float(request.form.get("price").replace(",", "."))
                in_tube = int(request.form.get("tube"))
                in_glutenfree = True if "glutenfree" in request.form else False
                in_lactosefree = True if "lactosefree" in request.form else False
                in_motortuning = 0
                properties = (in_name, in_price, in_tube, in_glutenfree, in_lactosefree, in_motortuning)
            elif self.endpoint_name == self.mm.mySQL.get_tbl_names().TBL_RECIPE:
                self.mm.logger.log(str(request.form))
                in_name = request.form.get("recipe_name")
                in_creator = 'None';
                in_ingredients = []
                for key, value in request.form.items():
                    if key[0:5] == 'irId_':
                        order = key[5:]
                        ingredient = {
                            'order': order,
                            'ir_id': value,
                            'ingredient_id': request.form.get("ingredientId_{}".format(order)),
                            'amount': request.form.get("amount_{}".format(order))
                        }
                        in_ingredients.append(ingredient)
                properties = (in_name, in_creator, in_ingredients)
            else:
                properties = ()

            self.mm.logger.log("Properties: " + str(properties))
            self.mm.logger.log("Count of prop.: " + str(len(properties)))

            # If properties are available, add new item
            if len(properties) > 0:
                if self.endpoint_name == self.mm.mySQL.get_tbl_names().TBL_RECIPE:
                    (recipe_name, recipe_creator, ingredients) = properties
                    recipe_properties = (recipe_name, recipe_creator)
                    success, item_id, err_msg = self.mm.mySQL.add_item(self.mm.mySQL.get_tbl_names().TBL_RECIPE,
                                                                       recipe_properties)
                    if success:
                        for ing in ingredients:
                            ing_properties = (ing['ingredient_id'], item_id, ing['amount'], ing['order'])
                            ir_success, ir_id, ir_err_msg = self.mm.mySQL.add_item(self.mm.mySQL.get_tbl_names().TBL_IR,
                                                                                   ing_properties)
                            if not ir_success:
                                success = False
                                err_msg = 'IR_UID {}: {}'.format(ir_id, ir_err_msg)
                                break

                else:
                    success, item_id, err_msg = self.mm.mySQL.add_item(self.endpoint_name, properties)

                # If adding new item was successful go to its single page or if not go to list page
                if success:
                    self.mm.logger.log("item_id : " + str(item_id))
                    return redirect(url_for(self.endpoint_name) + str(item_id) + "/")
                else:
                    self.mm.status.add_one_time_notification_error("Adding " + self.endpoint_name.title() + " failed. "
                                                                   + err_msg)
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
