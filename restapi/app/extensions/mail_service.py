import os
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

class MailService(object):
	def __init__(self, app=None):
		super(MailService, self).__init__()
		if app:
			self.app = app

	def init_app(self, app):
		self.app = app

	def send(self, _to_arr, _from, _subject, _body):
		try:
			# Send mail
			endpoint = '{}'.format(self.app.config['MAIL_SERVICE'])
			multipart_form_data = MultipartEncoder(
				fields= {
					'body': _body,
					'subject': _subject,
					'to[]': _to_arr,
					'from': _from
				}
			)
			res = requests.post(endpoint, data=multipart_form_data, headers={'Content-Type': multipart_form_data.content_type})

			if res.status_code > 400:
				print('Send mail is failed.')
			print 'Send mail result: {}'.format(res.json())
		except Exception as err:
			print("Failed to send mail: %s" % ( err))
