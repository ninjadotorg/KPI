from pyfcm import FCMNotification


class FirebaseCloudMessage(object):
	def __init__(self, app=None):
		super(FirebaseCloudMessage, self).__init__()
		if app:
			self.app = app
			self.push_service = FCMNotification(api_key=app.config['FCM_SERVER_KEY'])

	def init_app(self, app):
		self.app = app
		self.push_service = FCMNotification(api_key=app.config['FCM_SERVER_KEY'])

	def push_single_device(self, device_token, title, body, data_message):
		result = self.push_service.notify_single_device(registration_id=device_token, message_title=title, message_body=body, data_message=data_message)
		print result
		return result

	def push_multi_devices(self, devices, title, body, data_message):
		result = self.push_service.notify_multiple_devices(registration_ids=devices, message_title=title, message_body=body, data_message=data_message)
		print result
		return result
