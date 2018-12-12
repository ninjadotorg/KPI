# -*- coding: utf-8 -*-
import os
import sys
import hashlib
import json
import app.constants as CONST
import logging
import app.bl.answer as answer_bl

from flask import Blueprint, request, g
from app import db
from datetime import datetime
from sqlalchemy import and_, func

from app.models import Rating, Comment, User, ReviewType, Question
from app.helpers.message import MESSAGE, CODE
from app.helpers.decorators import admin_required, dev_required
from app.helpers.response import response_ok, response_error
from flask_jwt_extended import jwt_required, get_jwt_identity


answer_routes = Blueprint('answer', __name__)
logfile = logging.getLogger('file')


@answer_routes.route('/submit', methods=['POST'])
@jwt_required
def submit_answer():
	try:
		current_user = get_jwt_identity()
		user = db.session.query(User).filter(User.email==func.binary(current_user)).first()
		if user is None:
			return response_error(MESSAGE.USER_INVALID_EMAIL, CODE.USER_INVALID_EMAIL)
		
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)
			
		review_type = request.args.get('type', '')
		object_id = request.args.get('id', -1)
		
		if len(review_type) == 0 or \
			object_id == -1:
			return response_error(MESSAGE.ANSWER_INVALID_INPUT, CODE.ANSWER_INVALID_INPUT)

		result = answer_bl.is_valid_object_id(review_type, object_id)
		if result is False:
			return response_error(MESSAGE.ANSWER_INVALID_INPUT, CODE.ANSWER_INVALID_INPUT)

		if answer_bl.is_answer_question(user.id, review_type, object_id):
			return response_error(MESSAGE.ANSWER_QUESTION_ALREADY, CODE.ANSWER_QUESTION_ALREADY)

		
		rt = db.session.query(ReviewType).filter(ReviewType.name==func.binary(review_type)).first()
		ratings = data['ratings']
		if ratings is not None:
			for r in ratings:
				r = Rating(
					point=r['rating'],
					question_id=r['question_id'],
					object_id=object_id,
					user_id=user.id
				)
				db.session.add(r)
				db.session.flush()

		comment = data['comment']
		if comment is not None:
			c = Comment(
				desc=comment,
				user_id=user.id,
				object_id=object_id,
				type_id=rt.id
			)
			db.session.add(c)
			db.session.flush()

		return response_ok()
	except Exception, ex:
		return response_error(ex.message)


@answer_routes.route('/view', methods=['GET'])
@jwt_required
def view_answer():
	try:
		review_type = request.args.get('type', '')
		object_id = request.args.get('id', -1)
		
		if len(review_type) == 0 or \
			object_id == -1:
			return response_error(MESSAGE.ANSWER_INVALID_INPUT, CODE.ANSWER_INVALID_INPUT)

		result = answer_bl.is_valid_object_id(review_type, object_id)
		if result is False:
			return response_error(MESSAGE.ANSWER_INVALID_INPUT, CODE.ANSWER_INVALID_INPUT)

		rt = db.session.query(ReviewType).filter(ReviewType.name==func.binary(review_type)).first()
		response = {}

		# get all ratings
		ratings = db.session.query(Rating).filter(and_(Rating.object_id==object_id, Rating.question_id.in_(db.session.query(Question.id).filter(Question.type_id==rt.id)))).all()
		data = []
		for r in ratings:
			tmp = r.to_json()
			tmp['question'] = r.question.to_json()
			data.append(tmp)
		response['ratings'] = data

		# get comments
		comments = db.session.query(Comment).filter(and_(Comment.object_id==object_id, Comment.type_id==rt.id)).all()
		data = []
		for c in comments:
			data.append(c.to_json())
		response['comments'] = data

		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)