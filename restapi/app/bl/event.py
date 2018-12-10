from flask import g
from datetime import *

from app import db
from app.models import User, Handshake, Match
from app.helpers.utils import local_to_utc

import app.constants as CONST


def erc20_save_success_event():
	pass