from flask import Flask, session, render_template, request, jsonify, redirect, url_for
from flask.views import View, MethodView
from werkzeug import generate_password_hash
import json

from mmFlask.mmFlaskNav import mmFlaskNav

class mmFlask(Flask):
	def __init__(self, muesliMachine):
		super().__init__(__name__)

		self.muesliMachine = muesliMachine
		
		self.static_folder = "../static"
		self.template_folder = "../templates"
		
		self.nav = mmFlaskNav(self)

		self.registerUrlsDefault("index")
		self.registerUrlsDefault("signup")
		self.registerUrlsDefault("login")
		self.registerUrlsDefault("logout")

		# self.registerUrlsDefault("led")
		# self.registerUrlsDefault("scale")

		self.registerUrlsForItems("user")
		self.registerUrlsForItems("tube")
		self.registerUrlsForItems("ingredient")
		self.registerUrlsForItems("recipe")

		self.add_url_rule('/ajaxStatus', methods=['POST'], view_func=mmFlaskViewAjaxStatus.as_view('flaskAjaxStatus', muesliMachine=self.muesliMachine))
		self.add_url_rule('/ajaxSignUp', methods=['POST'], view_func=mmFlaskViewAjaxSignUp.as_view('flaskAjaxSignUp', muesliMachine=self.muesliMachine))
		
		# TODO: Keep this really secret:
		self.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

	def registerUrlsDefault(self, name):
		url = "/" + name + "/" if name != "index" else "/"
		viewFunc = mmFlaskViewDefaultRenderer.as_view(name, endpointName=name, muesliMachine=self.muesliMachine)
		self.add_url_rule(url, view_func=viewFunc)

	def registerUrlsForItems(self, name):
		url = "/" + name + "/"
		viewFunc = mmFlaskViewForItemsRenderer.as_view(name, endpointName=name, muesliMachine=self.muesliMachine)
		self.add_url_rule(url, defaults={"itemId": None}, view_func=viewFunc, methods=['GET',])
		self.add_url_rule(url, view_func=viewFunc, methods=['POST',])
		self.add_url_rule(url + "<int:itemId>", view_func=viewFunc, methods=['GET', 'PUT', 'DELETE'])
	
class mmFlaskViewDefaultRenderer(MethodView):
	def __init__(self, endpointName, muesliMachine):
		self.endpointName = endpointName
		self.templateName = endpointName + ".html"
		self.muesliMachine = muesliMachine
		super().__init__()
	
	def get(self):
		
		if self.endpointName == "logout":
			return self.logout()
		
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
			if self.muesliMachine.mySQL.spUsersCheckUserPassword(inUsername, inPassword) == True:
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
		self.muesliMachine = muesliMachine
		super().__init__()

	def get(self, itemId):
		if itemId is None:
			print("Show List of" + self.endpointName)
			# return a list of users
			return render_template(self.endpointName + "List.html")
		else:
			print("Show Single View of" + self.endpointName + "Id " + str(itemId))
			# expose a single user
			return render_template(self.endpointName + "Single.html", itemId=itemId)

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
		self.muesliMachine = muesliMachine
		super().__init__()
	
	def dispatch_request(self):
		cmd = request.form.get("cmd")

		if cmd and cmd != "":
			print(cmd)

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
				print("[WARN] cmd is not in JSON format")
			
			if parsed:		
				if "stepper" in cmd:
					stepperId = cmd["stepper"]["id"]
					steps = cmd["stepper"]["steps"]
					print("Stepper ID " + str(stepperId))
					print("Steps " + str(steps))
					self.muesliMachine.arduino.sendDrive(stepperId, steps)
				# Auskommentiert wg. Docker-Test
				# elif cmd == 'ledRedOn':
				# 	self.muesliMachine.ledRed.on()
				# elif cmd == 'ledRedOff':
				# 	self.muesliMachine.ledRed.off()
				# elif cmd == 'ledYellowOn':
				# 	self.muesliMachine.ledYellow.on()
				# elif cmd == 'ledYellowOff':
				# 	self.muesliMachine.ledYellow.off()
				# elif cmd == 'servo1On':
				# 	self.muesliMachine.servo1.on()
				# elif cmd == 'servo1Off':
				# 	self.muesliMachine.servo1.off()
				# elif cmd == 'tare':
				# 	self.muesliMachine.scale.tare()
			
		#print(scale.getAverage())
		return jsonify(self.muesliMachine.status.getStatus())
	
class mmFlaskViewAjaxSignUp(View):
	def __init__(self, muesliMachine):
		self.muesliMachine = muesliMachine
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
			msg = self.muesliMachine.mySQL.spUsersCreateUser(inUsername, inFirstname, inLastname, hashedPassword, inEmail, inRole)
			print(msg)
		else:
			self.muesliMachine.status.addOneTimeNotificationWarning("Enter all required fields")
		
		return jsonify(self.muesliMachine.status.getStatus())