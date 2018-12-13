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
from sqlalchemy import and_, func

from app.models import ReviewType, Question
from app.helpers.message import MESSAGE, CODE
from app.helpers.decorators import admin_required, hr_required, both_hr_and_amdin_required
from app.helpers.response import response_ok, response_error
from flask_jwt_extended import jwt_required
from app.constants import Type


question_routes = Blueprint('question', __name__)
logfile = logging.getLogger('file')


@question_routes.route('/list', methods=['GET'])
@jwt_required
def question_for_type():
	try:
		review_type = request.args.get('type', '')
		if len(review_type) == 0:
			return response_error(MESSAGE.TYPE_INVALID, CODE.TYPE_INVALID)

		t = db.session.query(ReviewType).filter(ReviewType.name==func.binary(review_type)).first()
		if t is None:
			return response_error(MESSAGE.TYPE_INVALID, CODE.TYPE_INVALID)

		
		questions = db.session.query(Question).filter(Question.type_id==t.id).all()
		response = []

		for question in questions:
			response.append(question.to_json())

		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)


@question_routes.route('/add', methods=['POST'])
@jwt_required
@both_hr_and_amdin_required
def add_quesion_for_type():
	"""
	"	admin will add questions for object type which need to be reviewed
	"""
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		review_type = request.args.get('type', '')
		if len(review_type) == 0:
			return response_error(MESSAGE.TYPE_INVALID, CODE.TYPE_INVALID)

		t = db.session.query(ReviewType).filter(ReviewType.name==func.binary(review_type)).first()
		if t is None:
			return response_error(MESSAGE.TYPE_INVALID, CODE.TYPE_INVALID)

		for d in data:
			if 'name' in d:
				question = Question(
					name=d['name'],
					type_id=t.id
				)
				db.session.add(question)
				db.session.flush()

		db.session.commit()
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@question_routes.route('/crud/<int:question_id>', methods=['PUT', 'DELETE'])
@jwt_required
@both_hr_and_amdin_required
def update_question_for_type(question_id):
	"""
	"	admin change question name for type
	"""
	try:
		review_type = request.args.get('type', '')
		if len(review_type) == 0:
			return response_error(MESSAGE.TYPE_INVALID, CODE.TYPE_INVALID)
		
		t = db.session.query(ReviewType).filter(ReviewType.name==func.binary(review_type)).first()
		if t is None:
			return response_error(MESSAGE.TYPE_INVALID, CODE.TYPE_INVALID)

		question = db.session.query(Question).filter(Question.id==question_id, Question.type_id==t.id).first()
		if question is None:
			return response_error(MESSAGE.QUESTION_NOT_EXIST, CODE.QUESTION_NOT_EXIST)

		if request.method == 'PUT':
			data = request.json
			if data is None:
				return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

			name = data.get('name', '')
			question.name = name

		else:
			db.session.delete(question)

		db.session.commit()
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)