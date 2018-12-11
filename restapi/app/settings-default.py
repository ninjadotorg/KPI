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
	SECRET_KEY = 'cryptosign'
	JWT_AUTH_USERNAME_KEY = 'email'
	JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=60)
	JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=120)
	
	# SendGrid
	SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')

class DevelopmentConfig(BaseConfig):
	SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/cryptosign?charset=utf8'


class TestingConfig(BaseConfig):
	SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/cryptosign?charset=utf8'


class StagingConfig(BaseConfig):
	ENV = 'DEV'
	BASE_URL = 'https://staging.ninja.org/'
	SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/cryptosign?charset=utf8'
	

class ProductionConfig(BaseConfig):
	ENV = 'PRODUCTION'
	BASE_URL = 'https://ninja.org/'
	SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/cryptosign?charset=utf8'