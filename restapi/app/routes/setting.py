import os
import json
import app.constants as CONST

from flask import Blueprint, request, current_app as app
from app.helpers.response import response_ok, response_error
from app.helpers.decorators import login_required, admin_required
from app import db
from app.models import Setting
from app.helpers.message import MESSAGE, CODE

setting_routes = Blueprint('setting', __name__)

@setting_routes.route('/', methods=['GET'])
@login_required
def settings():
	try:
		settings = Setting.query.all()
		data = []

		for setting in settings:
			data.append(setting.to_json())

		return response_ok(data)
	except Exception, ex:
		return response_error(ex.message)


@setting_routes.route('/add', methods=['POST'])
@login_required
@admin_required
def add():
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		settings = []
		response_json = []
		for item in data:
			setting = Setting(
				name=item['name'],
				status=item.get('status', 0),
				value=item.get('value', 0)
			)
			db.session.add(setting)
			db.session.flush()
			settings.append(setting)

			response_json.append(setting.to_json())

		db.session.commit()
		return response_ok(response_json)
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@setting_routes.route('/remove/<int:id>', methods=['POST'])
@login_required
@admin_required
def remove(id):
	try:
		setting = Setting.find_setting_by_id(id)
		if setting is not None:
			db.session.delete(setting)
			db.session.commit()
			return response_ok(message="{} has been deleted!".format(setting.id))
		else:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@setting_routes.route('/update/<int:id>', methods=['POST'])
@login_required
@admin_required
def update(id):
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		setting = Setting.find_setting_by_id(id)
		if setting is not None:
			status = int(data['status'])
			setting.status = status

			if 'value' in data:
				setting.value = data['value']

			db.session.commit()

			return response_ok(message='{} has been updated'.format(setting.id))
		else:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)