import os
import re
import json
import app.constants as CONST
import app.bl.storage as storage_bl

from flask import g
from flask import Blueprint, request, current_app as app
from sqlalchemy import and_, or_
from app.helpers.response import response_ok, response_error
from app.helpers.decorators import login_required
from app import db
from app.models import Source, Match, Outcome
from app.helpers.decorators import admin_required
from app.helpers.message import MESSAGE, CODE
from app.core import gc_storage_client
from app.helpers.utils import local_to_utc
from datetime import datetime

source_routes = Blueprint('source', __name__)

@source_routes.route('/', methods=['GET'])
@login_required
def sources():
	try:
		sources = Source.query.all()
		data = []

		for source in sources:
			data.append(source.to_json())

		return response_ok(data)
	except Exception, ex:
		return response_error(ex.message)


@source_routes.route('/add', methods=['POST'])
@login_required
def add():
	try:
		uid = int(request.headers['Uid'])
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		response_json = []
		for item in data:
			source = Source(
				name=item['name'],
				url=item['url'],
				created_user_id=uid
			)
			db.session.add(source)
			db.session.flush()

			response_json.append(source.to_json())
		db.session.commit()
		return response_ok(response_json)
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@source_routes.route('/remove/<int:id>', methods=['POST'])
@login_required
def remove(id):
	try:
		uid = int(request.headers['Uid'])
		source = db.session.query(Source).filter(and_(Source.id==id, Source.created_user_id==uid)).first()
		if source is not None:
			db.session.delete(source)
			db.session.commit()
			return response_ok(message="{} has been deleted!".format(source.id))
		else:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@source_routes.route('/update/<int:id>', methods=['POST'])
@login_required
def update(id):
	try:
		uid = int(request.headers['Uid'])
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		source = db.session.query(Source).filter(and_(Source.id==id, Source.created_user_id==uid)).first()
		if source is not None:
			source.name = data['name']
			source.url = data['url']
			db.session.commit()

			return response_ok(message='{} has been updated'.format(source.id))
		else:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@source_routes.route('/validate', methods=['POST'])
@login_required
def validate():
	try:
		uid = int(request.headers['Uid'])
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		name = data.get('name', '').strip()
		url = data.get('url', '').strip()
		source = db.session.query(Source).filter(and_(Source.name==name, Source.url==url)).first()
		if source is not None:
			return response_error(MESSAGE.SOURCE_EXISTED_ALREADY, CODE.SOURCE_EXISTED_ALREADY)
		else:
			return response_ok()

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@source_routes.route('/update/image/<int:source_id>', methods=['PUT'])
@admin_required
def update_image(source_id):
	try:
		source = Source.find_source_by_id(source_id)
		if source is None:
			return False

		request_size = request.headers.get('Content-length') # string
		is_update_matchs = request.form.get('update_matchs', '0') == '1'

		image_name = '{}_{}'.format(source.id, source.name).lower()
		image_name = re.sub(r'[^A-Za-z0-9\_\-\.]+', '_', image_name)
		image_name = '{}.jpg'.format(image_name)

		if request.files and len(request.files) > 0 and request.files['image'] is not None:
			if int(request_size) <= CONST.UPLOAD_MAX_FILE_SIZE and storage_bl.validate_extension(request.files['image'].filename, CONST.UPLOAD_ALLOWED_EXTENSIONS):
				image_name, saved_path = storage_bl.handle_upload_file(request.files['image'], file_name=image_name)
				saved_path, crop_saved_path = storage_bl.handle_crop_image(image_name, saved_path)
			else:
				return response_error(MESSAGE.FILE_TOO_LARGE, CODE.FILE_TOO_LARGE)

		if image_name is not None and saved_path is not None:
			result_upload = gc_storage_client.upload_to_storage(app.config.get('GC_STORAGE_BUCKET'), crop_saved_path, '{}/{}'.format(app.config.get('GC_STORAGE_FOLDER'), app.config.get('GC_DEFAULT_FOLDER')), image_name, True)
			if result_upload is False:
				return response_error()

		storage_bl.delete_file(crop_saved_path)
		storage_bl.delete_file(saved_path)

		# Update image_url all matchs
		if is_update_matchs:
			t = datetime.now().timetuple()
			seconds = local_to_utc(t)

			matches = db.session.query(Match)\
			.filter(\
				and_(\
					Match.source_id == source.id,
					or_(Match.image_url == None, Match.image_url == ""),
					Match.deleted == 0,\
					Match.date > seconds,\
					Match.public == 1,\
					Match.id.in_(db.session.query(Outcome.match_id).filter(and_(Outcome.result == -1, Outcome.hid != None)).group_by(Outcome.match_id))
				)\
			)\
			.all()

			image_url = CONST.SOURCE_GC_DOMAIN.format(app.config['GC_STORAGE_BUCKET'], '{}/{}'.format(app.config.get('GC_STORAGE_FOLDER'), app.config.get('GC_DEFAULT_FOLDER')), image_name)
			for match in matches:
				match.image_url = image_url
				db.session.flush()
			db.session.commit()

		return response_ok()

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
