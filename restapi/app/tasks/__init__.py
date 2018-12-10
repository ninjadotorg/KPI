from flask import Flask
from sqlalchemy import and_, func
from decimal import *
from datetime import datetime
from app.factory import make_celery
from app.core import db, configure_app, mail_services

import sys
import time
import app.constants as CONST
import os, hashlib
import requests
import random

app = Flask(__name__)
# config app
configure_app(app)

# db
db.init_app(app)

mail_services.init_app(app)
