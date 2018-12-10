import os
from datetime import timedelta


class BaseConfig(object):
	ENV = 'DEV'
	BASE_URL = ''
	BASE_DIR = os.path.abspath(os.path.dirname(__file__))
	UPLOAD_DIR = os.path.join(BASE_DIR, 'files', 'temp')

	# SQLALCHEMY
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/cryptosign?charset=utf8'
	DATABASE_CONNECT_OPTIONS = {'charset': 'utf8'}
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	# JWT
	JWT_AUTH_USERNAME_KEY = 'email'
	JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=60)
	JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=120)
	#
	SECRET_KEY = ''
	# SendGrid
	SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
	# AWS
	AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
	AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
	AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME', '')

	# Autonomous server: user sso
	DISPATCHER_SERVICE_ENDPOINT = os.getenv('DISPATCHER_SERVICE_ENDPOINT', '')
	
	# IPFS
	IPFS_REST_HOST = os.environ.get('IPFS_REST_HOST', 'localhost')
	IPFS_REST_PORT = os.environ.get('IPFS_REST_PORT', '5001')

	# ADMIN
	PASSPHASE = ''
	EMAIL = ''
	FROM_EMAIL = ''
	RESOLVER_EMAIL = ''

	FILE_FOLDER = os.path.dirname(os.path.realpath(__file__)) + '/files'


	REDIS_HOST = 'localhost'
	REDIS_PORT = 6379
	CELERY_BROKER_URL = 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)
	CELERY_RESULT_BACKEND = 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)

	# Dropbox
	DROPBOX_ACCESS_TOKEN = os.environ.get('DROPBOX_ACCESS_TOKEN', '')

	# SmartContract
	PREDICTION_SMART_CONTRACT = '0x123'
	PREDICTION_JSON = 'PredictionHandshake101'

	ERC20_PREDICTION_SMART_CONTRACT = '0x123'
	ERC20_PREDICTION_JSON = 'PredictionHandshakeWithToken'

	ERC20_TOKEN_REGISTRY_SMART_CONTRACT = '0x123'
	ERC20_TOKEN_REGISTRY_JSON = 'TokenRegistry'

	# Services
	FCM_SERVER_KEY = os.getenv('FCM_SERVER_KEY', '')
	SOLR_SERVICE = os.getenv('SOLR_SERVICE', '')
	FCM_SERVICE = os.getenv('FCM_SERVICE', 'http://localhost:8082')
	MAIL_SERVICE = os.getenv('MAIL_SERVICE', '')

	# Firebase
	FIREBASE_DATABASE_URL = ''
	FIREBASE_PROJECT_NAME = ''

	# GCloud
	GC_STORAGE_PROJECT_NAME = ''
	GC_STORAGE_BUCKET = ''
	GC_STORAGE_FOLDER = ''
	GC_DEFAULT_FOLDER = ''
	MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # limit max length of request

	# Algolia
	ALGOLIA_APPLICATION_ID = os.environ.get('ALGOLIA_APPLICATION_ID', '')
	ALGOLIA_API_KEY = os.environ.get('ALGOLIA_API_KEY', '')
	ALGOLIA_INDEX_NAME = os.environ.get('ALGOLIA_INDEX_NAME', '')

	# Recombee
	RECOMBEE_DB = ""
	RECOMBEE_KEY = ""

class DevelopmentConfig(BaseConfig):
	SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/cryptosign?charset=utf8'


class TestingConfig(BaseConfig):
	SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/cryptosign?charset=utf8'


class StagingConfig(BaseConfig):
	BASE_URL = ''
	SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/cryptosign?charset=utf8'
	REDIS_HOST = ''
	REDIS_PORT = 6379
	REDIS_PASSWORD = ''
	CELERY_BROKER_URL = 'redis://:%s@%s:%s/0' % (REDIS_PASSWORD, REDIS_HOST, REDIS_PORT)
	CELERY_RESULT_BACKEND = 'redis://:%s@%s:%s/0' % (REDIS_PASSWORD, REDIS_HOST, REDIS_PORT)
	SOLR_SERVICE = os.getenv('SOLR_SERVICE', '')
	
	FIREBASE_DATABASE_URL = ''
	FIREBASE_PROJECT_NAME = ''

	GC_STORAGE_PROJECT_NAME = ''
	GC_STORAGE_BUCKET = ''
	GC_STORAGE_FOLDER = ''
	GC_DEFAULT_FOLDER = ''

	RECOMBEE_DB = ""
	RECOMBEE_KEY = ""

class ProductionConfig(BaseConfig):
	BASE_URL = ''
	SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/cryptosign?charset=utf8'
	REDIS_HOST = ''
	REDIS_PORT = 6379
	CELERY_BROKER_URL = 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)
	CELERY_RESULT_BACKEND = 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)
	SOLR_SERVICE = os.getenv('SOLR_SERVICE', '')

	FIREBASE_DATABASE_URL = ''
	FIREBASE_PROJECT_NAME = ''

	GC_STORAGE_PROJECT_NAME = ''
	GC_STORAGE_BUCKET = ''
	GC_STORAGE_FOLDER = ''
	GC_DEFAULT_FOLDER = ''

	RECOMBEE_DB = ""
	RECOMBEE_KEY = ""