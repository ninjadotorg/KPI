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

from app.models import Role
from app.helpers.message import MESSAGE, CODE
from app.helpers.decorators import both_hr_and_amdin_required
from app.helpers.response import response_ok, response_error
from flask_jwt_extended import jwt_required


role_routes = Blueprint('role', __name__)
logfile = logging.getLogger('file')


@role_routes.route('/add', methods=['POST'])
@jwt_required
@both_hr_and_amdin_required
def add_role():
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		for d in data:
			if d.get('name', '').lower() in CONST.ROLES:
				r = Role(
					name=d.get('name', '').lower()
				)
				db.session.add(r)
				db.session.flush()
			else:
				return response_error(MESSAGE.ROLE_INVALID, CODE.ROLE_INVALID)

		db.session.commit()
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@role_routes.route('/list', methods=['GET'])
@jwt_required
@both_hr_and_amdin_required
def all_roles():
	try:
		rs = db.session.query(Role).all()
		response = []
		for r in rs:
			response.append(r.to_json())
			
		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)


@role_routes.route('/crud/<int:role_id>', methods=['PUT', 'DELETE'])
@jwt_required
@both_hr_and_amdin_required
def crud(role_id):
	try:

		role = Role.find_role_by_id(role_id)
		if role is None:
			return response_error(MESSAGE.ROLE_NOT_FOUND, CODE.ROLE_NOT_FOUND)

		if request.method == 'PUT':
			data = request.json
			if data is None:
				return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

			if 'name' in data and data['name'].lower() in CONST.ROLES:
				role.name = data['name'].lower()
				db.session.flush()

			else:
				return response_error(MESSAGE.ROLE_INVALID, CODE.ROLE_INVALID)

		else:
			db.session.delete(role)

		db.session.commit()
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)