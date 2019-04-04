from flask import Flask, session, render_template, request, jsonify, redirect, url_for
from flask.views import View, MethodView
from werkzeug import generate_password_hash

from mmFlask.mmFlaskNav import mmFlaskNav

class mmFlask(Flask):
	def __init__(self, muesliMachine):
		super().__init__(__name__)
		
		self.static_folder = "../static"
		self.template_folder = "../templates"
		
		self.nav = mmFlaskNav(self)
		
		self.add_url_rule('/', view_func=mmFlaskViewRenderer.as_view('flaskIndex',  endpointName='flaskIndex', muesliMachine=muesliMachine))
		self.add_url_rule('/led', view_func=mmFlaskViewRenderer.as_view('flaskLed', endpointName='flaskLed', templateName='led.html', muesliMachine=muesliMachine))
		self.add_url_rule('/scale', view_func=mmFlaskViewRenderer.as_view('flaskScale', endpointName='flaskScale', templateName='scale.html', muesliMachine=muesliMachine))
		self.add_url_rule('/signup', view_func=mmFlaskViewRenderer.as_view('flaskSignUp', endpointName='flaskSignUp', templateName='signup.html', muesliMachine=muesliMachine))
		self.add_url_rule('/login', view_func=mmFlaskViewRenderer.as_view('flaskLogIn', endpointName='flaskLogIn', templateName='login.html', muesliMachine=muesliMachine))
		self.add_url_rule('/logout', view_func=mmFlaskViewRenderer.as_view('flaskLogOut', endpointName='flaskLogOut', templateName='logout.html', muesliMachine=muesliMachine))
		self.add_url_rule('/ajaxStatus', methods=['POST'], view_func=mmFlaskViewAjaxStatus.as_view('flaskAjaxStatus', muesliMachine=muesliMachine))
		self.add_url_rule('/ajaxSignUp', methods=['POST'], view_func=mmFlaskViewAjaxSignUp.as_view('flaskAjaxSignUp', muesliMachine=muesliMachine))
		
		# set the secret key.  keep this really secret:
		self.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
	
class mmFlaskViewRenderer(MethodView):
	def __init__(self, endpointName, muesliMachine, templateName = 'index.html'):
		self.endpointName = endpointName
		self.templateName = templateName
		self.muesliMachine = muesliMachine
		super().__init__()
	
	def get(self):
		
		if self.endpointName == "flaskLogOut":
			return self.logout()
		
		else:
			return render_template(self.templateName)
		
	def post(self):        
		if self.endpointName == "flaskLogIn":
			return self.login()
		
		elif self.endpointName == "flaskLogOut":
			return self.logout()
		
		else:
			return ""
		
	def login(self):
		inUsername = request.form['inputUsername']
		inPassword = request.form['inputPassword']
		
		if inUsername and inPassword:
			if self.muesliMachine.mySQL.spUsersCheckUserPassword(inUsername, inPassword) == True:
				session['username'] = inUsername
				return redirect(url_for('flaskIndex'))
		
		return redirect(url_for('flaskLogIn'))
	
	def logout(self):
		if 'username' in session:
			session.pop('username', None)
		return redirect(url_for('flaskIndex'))
		

class mmFlaskViewAjaxStatus(View):       
	def __init__(self, muesliMachine):
		self.muesliMachine = muesliMachine
		super().__init__()
	
	def dispatch_request(self):
		cmd = request.form.get("cmd")
		print(cmd)
		# if cmd == 'ledRedOn':
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