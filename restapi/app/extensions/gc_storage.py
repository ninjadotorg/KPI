import os 

from google.cloud import storage
from google.oauth2 import service_account

dir_path = os.path.dirname(os.path.realpath(__file__))


class GoogleCloudStorage(object):
	def __init__(self, app=None):
		super(GoogleCloudStorage, self).__init__()
		if app:
			self.app = app
			self.init_gc_storage_client(app)


	def init_app(self, app):
		self.app = app
		self.init_gc_storage_client(app)


	def init_gc_storage_client(self, app):
		credentials = service_account.Credentials.from_service_account_file(dir_path + "/{}.json".format(app.config['GC_STORAGE_PROJECT_NAME']))
		credentials = credentials.with_scopes(['https://www.googleapis.com/auth/devstorage.full_control', 'https://www.googleapis.com/auth/devstorage.read_write'])
		self.gc_storage_client = storage.Client(project= app.config['GC_STORAGE_PROJECT_NAME'], credentials=credentials)


	def upload_to_storage(self, bucket_name, path_to_file_upload, blob_name, image_name, override=False):
		try:
			storage_client = self.gc_storage_client
			bucket = storage_client.get_bucket(bucket_name)
			if bucket.exists() is False:
				print "Bucket is not exist"
				return False
			
			# print [b.name for b in bucket.list_blobs()]
			blob = bucket.blob(blob_name + '/' + image_name)
			if blob.exists() is True:
				if override is False:
					print "Blod is exist: {}".format(blob_name + '/' + image_name)
					return False
				else:
					blob.delete()
					print('Blob {} deleted.'.format(blob_name + '/' + image_name))

			blob.upload_from_filename(path_to_file_upload, content_type='image/jpeg')
			# blob.make_public()
			uri = "gs://%s/%s/%s" % (bucket_name, blob_name, image_name)
			print "Upload load to Google Storage success: {}".format(uri)
			return True

		except Exception as err:
			print err
			print err.message
			print err.args
			print("upload_data to Google Storage error: %s" % (err))
