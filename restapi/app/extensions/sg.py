import sendgrid
import app.constants as CONST

# from sendgrid.helpers.mail import *

class SendGrid(object):
	def __init__(self, app=None):
		super(SendGrid, self).__init__()
		if app:
			self.app = app
			self.connection = sendgrid.SendGridAPIClient(apikey=app.config['SENDGRID_API_KEY'])

	def init_app(self, app):
		self.app = app
		self.connection = sendgrid.SendGridAPIClient(apikey=app.config['SENDGRID_API_KEY'])

	def send(self, fromEmail, toEmail, subject, content):
		if not self.connection:
			raise Exception('SendGrid connection is not initialized.')
		if len(content) > 0:
			data = {
				"personalizations": [
					{
						"to": [
							{
								"email": toEmail
							}
						],
						"subject": subject
					}
				],
				"from": {
					"email": fromEmail
				},
				"content": [
					{
						"type": "text/html",
						"value": content
					}
				]
			}
			try:
				response = self.connection.client.mail.send.post(request_body=data)
			except Exception as ex:
				print str(ex)
		else:
			print "Cannot send email for state = {}".format(state)

	def sendMany(self, fromEmail, toEmailArray, subject, content):
		if not self.connection:
			raise Exception('SendGrid connection is not initialized.')
		if len(content) > 0:
			data = {
				"personalizations": [
					{
						"to": toEmailArray,
						"subject": subject
					}
				],
				"from": {
					"email": fromEmail
				},
				"content": [
					{
						"type": "text/html",
						"value": content
					}
				]
			}
			try:
				response = self.connection.client.mail.send.post(request_body=data)
			except Exception as ex:
				print str(ex)
		else:
			print "Cannot send email for state = {}".format(state)
