# -*- coding: utf-8 -*-
import os
import sys
import hashlib
import json
import app.constants as CONST
import logging

from flask import Blueprint, request, g
from app import db
from datetime import datetime
from sqlalchemy import and_, func

from app.models import User
from app.helpers.message import MESSAGE, CODE
from app.helpers.decorators import admin_required
from app.helpers.response import response_ok, response_error
from flask_jwt_extended import jwt_required


people_routes = Blueprint('people', __name__)
logfile = logging.getLogger('file')


@people_routes.route('/list', methods=['GET'])
@jwt_required
def all_people():
	try:
		page = int(request.args.get('page', 0))
		offset = int(request.args.get('offset', 10))
		rows = db.session.query(func.count(User.id)).scalar()
		users = db.session.query(User) \
				.filter() \
				.limit(offset) \
				.offset(page*offset) \
				.all()

		response = {}
		response['total'] = rows / offset + 1

		data = []
		for u in users:
			data.append(u.to_json())

		response['people'] = data
		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)
