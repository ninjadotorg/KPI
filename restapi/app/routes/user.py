# -*- coding: utf-8 -*-
import os
import sys
import json
import hashlib
import requests

import app.constants as CONST
import app.bl.storage as storage_bl
import app.bl.user as user_bl

from sqlalchemy import func
from flask import Blueprint, request, g
from app import db
from datetime import datetime
from flask_jwt_extended import (create_access_token, jwt_required, get_jwt_identity)

from app.core import gc_services
from app.models import User, ReviewType, Role
from app.helpers.utils import is_valid_email, is_valid_password, local_to_utc
from app.helpers.decorators import both_hr_and_amdin_required, admin_required
from app.helpers.message import MESSAGE, CODE
from app.helpers.response import response_ok, response_error


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
@jwt_required
@both_hr_and_amdin_required
def sign_up():
	try:
		saved_path = None
		image_name = None
		email = request.form.get('email', '')
		password = request.form.get('password', '')
		name = request.form.get('name', '')
		title = request.form.get('title', '')
		if is_valid_email(email) == False:
			return response_error(MESSAGE.USER_INVALID_EMAIL, CODE.USER_INVALID_EMAIL)

		if is_valid_password(password) == False:
			return response_error(MESSAGE.USER_INVALID_PASSWORD, CODE.USER_INVALID_PASSWORD)

		t = db.session.query(ReviewType).filter(ReviewType.name==CONST.Type['People']).first()
		if t is None:
			return response_error(MESSAGE.TYPE_NOT_IN_DATABASE, CODE.TYPE_NOT_IN_DATABASE)

		u = User.find_user_by_email(email)	
		if u is None:
			request_size = request.headers.get('Content-length')
			if request.files and len(request.files) > 0 and request.files['avatar'] is not None:
				if int(request_size) <= CONST.UPLOAD_MAX_FILE_SIZE and storage_bl.validate_extension(request.files['avatar'].filename, CONST.UPLOAD_ALLOWED_EXTENSIONS):
					time = datetime.now().timetuple()
					seconds = local_to_utc(time)
					image_name = '{}_{}'.format(seconds, request.files['avatar'].filename)
					saved_path = storage_bl.handle_upload_file(request.files['avatar'], file_name=image_name)
					
				else:
					return response_error(MESSAGE.FILE_TOO_LARGE, CODE.FILE_TOO_LARGE)
			
			gc_services.upload_to_storage(g.GC_STORAGE_BUCKET, saved_path, g.GC_STORAGE_FOLDER, image_name)
			u = User(
				name=name,
				email=email,
				password=hashlib.md5(password).hexdigest(),
				type_id=t.id,
				title=title,
				avatar='{}{}'.format(CONST.BASE_IMAGE_URL, image_name) if image_name is not None else None
			)
			db.session.add(u)
			db.session.flush()
		else:
			return response_error(MESSAGE.USER_EMAIL_EXIST_ALREADY, CODE.USER_EMAIL_EXIST_ALREADY)

		response = u.to_json()
		response['access_token'] = create_access_token(identity=email, fresh=True)
		db.session.commit()

		storage_bl.delete_file(saved_path)
		return response_ok(response)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)



@user_routes.route('/update-user/<int:user_id>', methods=['PUT'])
@jwt_required
@both_hr_and_amdin_required
def update_user(user_id):
	try:
		u = User.find_user_by_id(user_id)
		if u is None:
			return response_error(MESSAGE.USER_INVALID, CODE.USER_INVALID)

		email = request.form.get('email', '')
		password = request.form.get('password', '')
		name = request.form.get('name', '')
		title = request.form.get('title', '')
		role_id = request.form.get('role_id')

		t = db.session.query(ReviewType).filter(ReviewType.name==CONST.Type['People']).first()
		if t is None:
			return response_error(MESSAGE.TYPE_NOT_IN_DATABASE, CODE.TYPE_NOT_IN_DATABASE)

		if len(email) > 0:
			if is_valid_email(email) == False or \
				User.find_user_by_email(email) is not None:
				return response_error(MESSAGE.USER_INVALID_EMAIL, CODE.USER_INVALID_EMAIL)
			u.email = email

		if len(password) > 0:
			if is_valid_password(password) == False:
				return response_error(MESSAGE.USER_INVALID_PASSWORD, CODE.USER_INVALID_PASSWORD)
			u.password = password

		if len(name) > 0:
			u.name = name

		if len(title) > 0:
			u.title = title

		if role_id is not None and \
			Role.find_role_by_id(role_id) is not None:
			u.role_id = role_id

		request_size = request.headers.get('Content-length')
		if request.files and len(request.files) > 0 and request.files['avatar'] is not None:
			if int(request_size) <= CONST.UPLOAD_MAX_FILE_SIZE and storage_bl.validate_extension(request.files['avatar'].filename, CONST.UPLOAD_ALLOWED_EXTENSIONS):
				time = datetime.now().timetuple()
				seconds = local_to_utc(time)
				image_name = '{}_{}'.format(seconds, request.files['avatar'].filename)
				saved_path = storage_bl.handle_upload_file(request.files['avatar'], file_name=image_name)
				
			else:
				return response_error(MESSAGE.FILE_TOO_LARGE, CODE.FILE_TOO_LARGE)
			
			gc_services.upload_to_storage(g.GC_STORAGE_BUCKET, saved_path, g.GC_STORAGE_FOLDER, image_name)
			u.avatar = '{}{}'.format(CONST.BASE_IMAGE_URL, image_name)
			

		db.session.commit()
		return response_ok(u.to_json())

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)



@user_routes.route('/delete-user/<int:user_id>', methods=['DELETE'])
@jwt_required
@both_hr_and_amdin_required
def delete_user(user_id):
	try:
		u = User.find_user_by_id(user_id)
		if u is None:
			return response_error(MESSAGE.USER_INVALID, CODE.USER_INVALID)

		db.session.delete(u)
		db.session.commit()
		return response_ok()

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@user_routes.route('/change-password', methods=['POST'])
@jwt_required
def change_password():
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		current_user = get_jwt_identity()
		user = db.session.query(User).filter(User.email==func.binary(current_user)).first()
		if user is None:
			return response_error(MESSAGE.USER_INVALID_EMAIL, CODE.USER_INVALID_EMAIL)

		current_password = data.get('current_password', '')
		new_password = data.get('new_password', '')

		current_password = hashlib.md5(current_password).hexdigest()

		if is_valid_password(new_password) == False:
			return response_error(MESSAGE.USER_INVALID_PASSWORD, CODE.USER_INVALID_PASSWORD)

		if user.password == current_password:
			user.password = hashlib.md5(new_password).hexdigest()
			user.is_need_change_password = 0
		else:
			return response_error(MESSAGE.USER_INVALID_PASSWORD, CODE.USER_INVALID_PASSWORD)

		db.session.flush()
		db.session.commit()
		return response_ok()

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@user_routes.route('/import-user', methods=['GET'])
@admin_required
def import_user():
	try:
		users = user_bl.read_data()
		db.session.bulk_save_objects(users)
		return response_ok()

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@user_routes.route('/add', methods=['GET'])
@admin_required
def add():
	try:
		users = db.session.query(User).all()
		for u in users:
			normalized_words = user_bl.no_accent_vietnamese(u.name)
			u.keywords = normalized_words
			db.session.flush()
		
		db.session.commit()
		return response_ok()

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)