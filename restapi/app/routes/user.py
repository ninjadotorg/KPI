# -*- coding: utf-8 -*-
import os
import sys
import json
import hashlib
import requests

from flask import Blueprint, request, g
from app import db
from datetime import datetime
from flask_jwt_extended import (create_access_token)

from app.models import User, ReviewType
from app.helpers.utils import is_valid_email, is_valid_password
from app.helpers.message import MESSAGE, CODE
from app.helpers.response import response_ok, response_error
from app.constants import Type


user_routes = Blueprint('user', __name__)

@user_routes.route('/auth', methods=['POST'])
def auth():
	try:
		data = request.json
		if data is None or 'email' not in data:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		email = data['email']
		password = data['password']
		if is_valid_email(email) == False:
			return response_error(MESSAGE.USER_INVALID_EMAIL, CODE.USER_INVALID_EMAIL)

		if is_valid_password(password) == False:
			return response_error(MESSAGE.USER_INVALID_PASSWORD, CODE.USER_INVALID_PASSWORD)
		
		password = hashlib.md5(password).hexdigest()
		u = User.find_user_by_email_and_password(email, password)
		if u is not None:
			response = u.to_json()
			response['access_token'] = create_access_token(identity=email, fresh=True)
			return response_ok(response)

		return response_error(MESSAGE.USER_INVALID, CODE.USER_INVALID)
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@user_routes.route('/sign-up', methods=['POST'])
def sign_up():
	try:
		data = request.json
		if data is None or 'email' not in data:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		email = data['email']
		password = data['password']
		name = data.get('name', '')
		if is_valid_email(email) == False:
			return response_error(MESSAGE.USER_INVALID_EMAIL, CODE.USER_INVALID_EMAIL)

		if is_valid_password(password) == False:
			return response_error(MESSAGE.USER_INVALID_PASSWORD, CODE.USER_INVALID_PASSWORD)

		t = db.session.query(ReviewType).filter(Type['People']).first()
		if t is None:
			return response_error(MESSAGE.TYPE_NOT_IN_DATABASE, CODE.TYPE_NOT_IN_DATABASE)

		u = User.find_user_by_email(email)	
		if u is None:
			u = User(
				name=name,
				email=email,
				password=hashlib.md5(password).hexdigest(),
				type_id=t.id
			)
			db.session.add(u)
			db.session.flush()
		else:
			return response_error(MESSAGE.USER_EMAIL_EXIST_ALREADY, CODE.USER_EMAIL_EXIST_ALREADY)

		response = u.to_json()
		response['access_token'] = create_access_token(identity=email, fresh=True)
		db.session.commit()
		return response_ok(response)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
