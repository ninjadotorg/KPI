# -*- coding: utf-8 -*-
import os
import sys
import hashlib
import json
import app.constants as CONST
import logging

from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required
from app import db, sg
from datetime import datetime
from sqlalchemy import and_, func

from app.models import Project, ReviewType
from app.helpers.message import MESSAGE, CODE
from app.helpers.decorators import admin_required, dev_required
from app.helpers.response import response_ok, response_error
from app.constants import Type

project_routes = Blueprint('project', __name__)
logfile = logging.getLogger('file')


@project_routes.route('/list', methods=['GET'])
@jwt_required
def all_projects():
	try:
		page = int(request.args.get('page', 0))
		offset = int(request.args.get('offset', 10))

		rows = db.session.query(func.count(Project.id)).scalar()

		projects = db.session.query(Project) \
					.filter() \
					.limit(offset) \
					.offset(page*offset) \
					.all()

		response = {}
		response['total'] = rows / offset + 1

		data = []
		for p in projects:
			data.append(p.to_json())

		response['projects'] = data
		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)


@project_routes.route('/add', methods=['POST'])
@admin_required
def add_project():
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		t = db.session.query(ReviewType).filter(ReviewType.name==Type['Project']).first()
		if t is None:
			return response_error(MESSAGE.TYPE_NOT_IN_DATABASE, CODE.TYPE_NOT_IN_DATABASE)
		
		for d in data:
			if 'name' in d:
				project = Project(
					name=d['name'],
					type_id=t.id
				)
				db.session.add(project)
				db.session.flush()

		db.session.commit()
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)