from flask import Flask, session, render_template, request, jsonify, redirect, url_for
from flask.views import View, MethodView
from werkzeug import generate_password_hash
import json

from mmFlask.mmFlaskNav import mmFlaskNav

class mmFlask(Flask):
	def __init__(self, muesliMachine):
		super().__init__(__name__)

		self.mm = muesliMachine
		
		self.static_folder = "../static"
		self.template_folder = "../templates"
		
		self.nav = mmFlaskNav(self)

		self.registerUrlsDefault("index")
		self.registerUrlsDefault("status") # TODO: Multithreading -> Status auf schon laufender Webpage anzeigen
		self.registerUrlsDefault("signup")
		self.registerUrlsDefault("login")
		self.registerUrlsDefault("logout")

		# self.registerUrlsDefault("led")
		# self.registerUrlsDefault("scale")

		self.registerUrlsForItems("user")
		self.registerUrlsForItems("tube")
		self.registerUrlsForItems("ingredient")
		self.registerUrlsForItems("recipe")

		self.add_url_rule('/ajaxStatus', methods=['POST'], view_func=mmFlaskViewAjaxStatus.as_view('flaskAjaxStatus', muesliMachine=self.mm))
		self.add_url_rule('/ajaxSignUp', methods=['POST'], view_func=mmFlaskViewAjaxSignUp.as_view('flaskAjaxSignUp', muesliMachine=self.mm))
		
		# TODO: Keep this really secret:
		self.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

	def registerUrlsDefault(self, name):
		url = "/" + name + "/" if name != "index" else "/"
		viewFunc = mmFlaskViewDefaultRenderer.as_view(name, endpointName=name, muesliMachine=self.mm)
		self.add_url_rule(url, view_func=viewFunc)

	def registerUrlsForItems(self, name):
		url = "/" + name + "/"
		viewFunc = mmFlaskViewForItemsRenderer.as_view(name, endpointName=name, muesliMachine=self.mm)
		self.add_url_rule(url, defaults={"itemId": None}, view_func=viewFunc, methods=['GET',])
		self.add_url_rule(url, view_func=viewFunc, methods=['POST',])
		self.add_url_rule(url + "<int:itemId>/", view_func=viewFunc, methods=['GET', 'PUT', 'DELETE'])
	
class mmFlaskViewDefaultRenderer(MethodView):
	def __init__(self, endpointName, muesliMachine):
		self.endpointName = endpointName
		self.templateName = endpointName + ".html"
		self.mm = muesliMachine
		super().__init__()
	
	def get(self):
		
		if self.endpointName == "logout":
			return self.logout()
		elif self.endpointName == "status":
			return render_template(self.templateName, status=self.mm.status.getStatus())
		else:
			return render_template(self.templateName)
		
	def post(self):        
		if self.endpointName == "login":
			return self.login()
		
		elif self.endpointName == "logout":
			return self.logout()
		
		else:
			return ""
		
	def login(self):
		inUsername = request.form['inputUsername']
		inPassword = request.form['inputPassword']
		
		if inUsername and inPassword:
			if self.mm.mySQL.spUsersCheckUserPassword(inUsername, inPassword) == True:
				session['username'] = inUsername
				return redirect(url_for('index'))
		
		return redirect(url_for('login'))
	
	def logout(self):
		if 'username' in session:
			session.pop('username', None)
		return redirect(url_for('index'))


class mmFlaskViewForItemsRenderer(MethodView):
	def __init__(self, endpointName, muesliMachine):
		self.endpointName = endpointName
		self.mm = muesliMachine
		super().__init__()

	def get(self, itemId):
		if itemId is None:
			self.mm.logger.log("Show List of " + self.endpointName)
			items = self.mm.mySQL.getItems(self.endpointName)
			return render_template(self.endpointName + "List.html", items=items)
		else:
			self.mm.logger.log("Show Single View of " + self.endpointName + "Id " + str(itemId))
			item = self.mm.mySQL.getItemById(self.endpointName, itemId)
			return render_template(self.endpointName + "Single.html", item=item)

	def post(self):
		# create a new user
		pass

	def delete(self, itemId):
		# delete a single user
		pass

	def put(self, itemId):
		# update a single user
		pass


class mmFlaskViewAjaxStatus(View):       
	def __init__(self, muesliMachine):
		self.mm = muesliMachine
		super().__init__()
	
	def dispatch_request(self):
		cmd = request.form.get("cmd")
		requestId = request.form.get("id")
		self.mm.logger.log("Request ID: " + str(requestId))

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
				self.mm.logger.logErr("cmd is not in JSON format")
			
			if parsed:		
				if "stepper" in cmd:
					stepperId = cmd["stepper"]["id"]
					steps = cmd["stepper"]["steps"]
					self.mm.logger.log("Stepper ID " + str(stepperId))
					self.mm.logger.log("Steps " + str(steps))
					self.mm.arduino.sendDrive(stepperId, steps)
				# Auskommentiert wg. Docker-Test
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
			
		#self.mm.logger.log(scale.getAverage())
		return jsonify(self.mm.status.getStatus(requestId))
	
class mmFlaskViewAjaxSignUp(View):
	def __init__(self, muesliMachine):
		self.mm = muesliMachine
		super().__init__()
		
	def dispatch_request(self):
		inFirstname = request.form.get("inputFirstname")
		inLastname = request.form.get("inputLastname")
		inUsername = request.form.get("inputUsername")
		inEmail = request.form.get("inputEmail")
		inPassword = request.form.get("inputPassword")
		hashedPassword = generate_password_hash(inPassword)
		inRole = "admin"
		
		if inUsername and inEmail and inPassword:
			msg = self.mm.mySQL.spUsersCreateUser(inUsername, inFirstname, inLastname, hashedPassword, inEmail, inRole)
			self.mm.logger.log(msg)
		else:
			self.mm.status.addOneTimeNotificationWarning("Enter all required fields")
		
		return jsonify(self.mm.status.getStatus())