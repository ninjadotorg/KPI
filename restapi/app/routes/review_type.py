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

from app.models import ReviewType
from app.helpers.message import MESSAGE, CODE
from app.helpers.decorators import admin_required, dev_required
from app.helpers.response import response_ok, response_error
from flask_jwt_extended import jwt_required


type_routes = Blueprint('type', __name__)
logfile = logging.getLogger('file')


@type_routes.route('/list', methods=['GET'])
@jwt_required
def all_types():
	try:
		rs = db.session.query(ReviewType).all()
		response = []
		for r in rs:
			response.append(r.to_json())

		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)


@type_routes.route('/add', methods=['POST'])
@admin_required
def add_type():
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		for d in data:
			if 'name' in d:
				r = ReviewType(
					name=d['name']
				)
				db.session.add(r)
				db.session.flush()

		db.session.commit()
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
