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
from sqlalchemy import and_

from app.models import Company, ReviewType
from app.helpers.message import MESSAGE, CODE
from app.helpers.decorators import both_hr_and_amdin_required, admin_required
from app.helpers.response import response_ok, response_error
from app.constants import Type


company_routes = Blueprint('company', __name__)
logfile = logging.getLogger('file')


@company_routes.route('/list', methods=['GET'])
@jwt_required
def all_companies():
	try:
		cs = db.session.query(Company).all()
		response = []
		for c in cs:
			tmp = c.to_json()
			response.append(tmp)
			
		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)


@company_routes.route('/add', methods=['POST'])
@jwt_required
@both_hr_and_amdin_required
def add_company():
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		t = db.session.query(ReviewType).filter(ReviewType.name==Type['Company']).first()
		if t is None:
			return response_error(MESSAGE.TYPE_NOT_IN_DATABASE, CODE.TYPE_NOT_IN_DATABASE)
		
		for d in data:
			if 'name' in d:
				company = Company(
					name=d['name'],
					type_id=t.id
				)
				db.session.add(company)
				db.session.flush()

		db.session.commit()
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@company_routes.route('/crud/<int:company_id>', methods=['PUT', 'DELETE'])
@jwt_required
@both_hr_and_amdin_required
def crud(company_id):
	try:
		company = Company.find_company_by_id(company_id)
		if company is None:
			return response_error(MESSAGE.COMPANY_NOT_FOUND, CODE.COMPANY_NOT_FOUND)

		if request.method == 'PUT':
			data = request.json
			if data is None:
				return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

			if 'name' in data:
				company.name = data['name']
				db.session.flush()

		else:
			db.session.delete(company)

		db.session.commit()
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@company_routes.route('/update-counting-number', methods=['GET'])
@admin_required
def update_rating_and_comment_count():
	try:
		companies = db.session.query(Company).all()
		for c in companies:
			rating_count = people_bl.count_rating_for_object(c, CONST.Type['Company'])
			comment_count = people_bl.count_comments_for_object(c, CONST.Type['Company'])

			c.comment_count = comment_count
			c.rating_count = rating_count
			db.session.flush()

		db.session.commit()
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)