import os
import dropbox

class DropboxService(object):
	def __init__(self, app=None):
		super(DropboxService, self).__init__()
		if app:
			self.app = app
			self.dbox = Dropbox(app.config['DROPBOX_ACCESS_TOKEN'])

	def init_app(self, app):
		self.app = app
		self.dbox = dropbox.Dropbox(app.config['DROPBOX_ACCESS_TOKEN'])

	def upload(self, from_file_path, to_file_path):
		try:
			with open(from_file_path, 'rb') as f:
				self.dbox.files_upload(f.read(), to_file_path, mode=dropbox.files.WriteMode('overwrite'))
		except Exception as err:
			print("Failed to upload %s\n%s" % (from_file_path, err))
