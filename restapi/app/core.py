import os

from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

from app.extensions.ipfs import IPFS
from app.extensions.sg import SendGrid
from app.extensions.s3 import AWSS3
from app.extensions.water_mark import WaterMark
from app.extensions.fcm import FirebaseCloudMessage
from app.extensions.firebase_db import FirebaseDatabase
from app.extensions.dropbox_service import DropboxService
from app.extensions.mail_service import MailService
from app.extensions.algolia import Algolia
from app.extensions.gc_storage import GoogleCloudStorage
from app.extensions.recombee import Recombee
from app.extensions.slack import SlackService

db = SQLAlchemy()
jwt = JWTManager()
s3 = AWSS3()
sg = SendGrid()
wm = WaterMark()
fcm = FirebaseCloudMessage()
ipfs = IPFS()
firebase = FirebaseDatabase()
dropbox_services = DropboxService()
mail_services = MailService()
algolia = Algolia()
gc_storage_client = GoogleCloudStorage()
recombee_client = Recombee()
slack_service = SlackService()

# configure app from env + silent local settings.cfg
def configure_app(app):
	
	base_dir = os.path.abspath(os.path.dirname(__file__))
	if not os.path.exists(base_dir + "/settings.py"):
		os.rename(base_dir + "/settings-default.py", base_dir + "/settings.py")	

	if not os.path.exists(base_dir + "/settings.cfg"):
		os.rename(base_dir + "/settings-default.cfg", base_dir + "/settings.cfg")	
	
	config = {
		"development": "app.settings.DevelopmentConfig",
		"testing": "app.settings.TestingConfig",
		"staging": "app.settings.StagingConfig",
		"production": "app.settings.ProductionConfig",
		"default": "app.settings.DevelopmentConfig"
	}	
	config_name = os.getenv('PYTHON_ENV', 'default')
	app.config.from_object(config[config_name])  # object-based default configuration
	app.config.from_pyfile(os.path.dirname(os.path.realpath(__file__)) + '/settings.cfg', silent=True)  # instance-folders configuration
