import boto
import boto.s3
from boto.s3.key import Key
import os, hashlib
import time

from werkzeug.utils import secure_filename


class AWSS3(object):
	def __init__(self, app=None):
		super(AWSS3, self).__init__()
		if app:
			self.app = app
			self.connection = boto.connect_s3(app.config['AWS_ACCESS_KEY_ID'], app.config['AWS_SECRET_ACCESS_KEY'])

	def init_app(self, app):
		self.app = app
		self.connection = boto.connect_s3(app.config['AWS_ACCESS_KEY_ID'], app.config['AWS_SECRET_ACCESS_KEY'])

	def generate_url(self, file, filename = None):
		bucket = self.get_bucket()
		millis = int(round(time.time()))
		k = Key(bucket)
		k.key = filename if filename else '{}_{}.pdf'.format(millis, hashlib.md5(os.urandom(32)).hexdigest())
		k.metadata['Content-Type'] = 'application/pdf'

		url = k.generate_url(expires_in=0, query_auth=False)
		return k, url

	def get_bucket(self):
		if not self.connection:
			raise Exception('S3 connection is not initialized.')
		return self.connection.get_bucket(self.app.config['AWS_BUCKET_NAME'])

	def save_file_to_local(self, file):
		millis = int(round(time.time()))
		filename = secure_filename(file.filename)
		extension = os.path.splitext(filename)[1]
		destination = '{}_{}{}'.format(millis, hashlib.md5(os.urandom(32)).hexdigest(), extension)
		path = os.path.join(self.app.config['UPLOAD_DIR'], destination)
		result = file.save(path)
		return destination, filename, extension

	def upload_local_file_to_s3(self, destination, extension):
		path = os.path.join(self.app.config['UPLOAD_DIR'], destination)
		k = Key(self.get_bucket())
		k.key = destination
		if extension.endswith('pdf'):
			k.metadata['Content-Type'] = 'application/pdf'
		k.set_contents_from_filename(path)
		url = k.generate_url(expires_in=0, query_auth=False)
		os.unlink(path)

		return url
