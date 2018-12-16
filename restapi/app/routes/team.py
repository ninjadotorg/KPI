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
		rows = db.session.query(func.count(Team.id)).scalar()

		teams = db.session.query(Team) \
				.filter() \
				.limit(10) \
				.offset(page*10) \
				.all()

		response = {}
		response['total'] = rows / 10 + 1

		data = []
		for t in teams:
			data.append(t.to_json())

		response['teams'] = data
		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)


@team_routes.route('/add', methods=['POST'])
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
