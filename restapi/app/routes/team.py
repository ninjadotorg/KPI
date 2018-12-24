# -*- coding: utf-8 -*-
import os
import sys
import hashlib
import json
import app.constants as CONST
import logging

import app.bl.people as people_bl

from flask import Blueprint, request, g
from flask_jwt_extended import jwt_required
from app import db, sg
from datetime import datetime
from sqlalchemy import and_, func

from app.models import Team, ReviewType
from app.helpers.message import MESSAGE, CODE
from app.helpers.decorators import both_hr_and_amdin_required
from app.helpers.response import response_ok, response_error
from app.constants import Type


team_routes = Blueprint('team', __name__)
logfile = logging.getLogger('file')


@team_routes.route('/list', methods=['GET'])
@jwt_required
def all_teams():
	try:
		page = request.args.get('page', 0)
		offset = int(request.args.get('offset', 10))
		rows = db.session.query(func.count(Team.id)).scalar()

		teams = db.session.query(Team) \
				.filter() \
				.limit(offset) \
				.offset(page*offset) \
				.all()

		response = {}
		response['total'] = rows / offset + 1

		data = []
		for t in teams:
			tmp = t.to_json()
			tmp['rating'] = people_bl.count_rating_for_object(t, CONST.Type['Team'])
			data.append(tmp)

		response['teams'] = data
		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)


@team_routes.route('/add', methods=['POST'])
@jwt_required
@both_hr_and_amdin_required
def add_team():
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		t = db.session.query(ReviewType).filter(ReviewType.name==Type['Team']).first()
		if t is None:
			return response_error(MESSAGE.TYPE_NOT_IN_DATABASE, CODE.TYPE_NOT_IN_DATABASE)
		
		for d in data:
			if 'name' in d:
				team = Team(
					name=d['name'],
					type_id=t.id
				)
				db.session.add(team)
				db.session.flush()

		db.session.commit()
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@team_routes.route('/crud/<int:team_id>', methods=['PUT', 'DELETE'])
@jwt_required
@both_hr_and_amdin_required
def crud(team_id):
	try:
		t = Team.find_team_by_id(team_id)
		if t is None:
			return response_error(MESSAGE.TEAM_NOT_FOUND, CODE.TEAM_NOT_FOUND)

		if request.method == 'PUT':
			data = request.json
			if data is None:
				return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

			if 'name' in data:
				t.name = data['name']
				db.session.flush()
		else:
			db.session.delete(t)

		db.session.commit()
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
