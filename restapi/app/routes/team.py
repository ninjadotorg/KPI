# -*- coding: utf-8 -*-
import os
import sys
import hashlib
import json
import app.constants as CONST
import logging

from flask import Blueprint, request, g
from app import db, sg
from datetime import datetime
from sqlalchemy import and_

from app.helpers.message import MESSAGE, CODE
from app.helpers.decorators import admin_required, dev_required
from app.helpers.response import response_ok, response_error
from flask_jwt_extended import jwt_required


team_routes = Blueprint('team', __name__)
logfile = logging.getLogger('file')


@team_routes.route('/list', methods=['GET'])
@jwt_required
def all_teams():
	try:
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@team_routes.route('/add', methods=['POST'])
@admin_required
def add_team():
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
