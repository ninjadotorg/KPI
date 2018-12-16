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
from app.helpers.decorators import admin_required
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
				rating = Rating(
					point=r['rating'],
					question_id=r['question_id'],
					object_id=object_id,
					user_id=user.id
				)
				db.session.add(rating)
				db.session.flush()

				comment = r['comment']
				if comment is not None:
					c = Comment(
						desc=comment,
						rating_id=rating.id
					)
					db.session.add(c)
					db.session.flush()

		else:
			return response_error(MESSAGE.ANSWER_INVALID_INPUT, CODE.ANSWER_INVALID_INPUT)	

		db.session.commit()
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@answer_routes.route('/view', methods=['GET'])
@jwt_required
def view_answer():
	try:
		review_type = request.args.get('type', '')
		object_id = request.args.get('id', -1)
		current_user = get_jwt_identity()
		user = db.session.query(User).filter(User.email==func.binary(current_user)).first()
		if user is None:
			return response_error(MESSAGE.USER_INVALID_EMAIL, CODE.USER_INVALID_EMAIL)
		
		if len(review_type) == 0 or \
			object_id == -1:
			return response_error(MESSAGE.ANSWER_INVALID_INPUT, CODE.ANSWER_INVALID_INPUT)

		result = answer_bl.is_valid_object_id(review_type, object_id)
		if result is False:
			return response_error(MESSAGE.ANSWER_INVALID_INPUT, CODE.ANSWER_INVALID_INPUT)

		rt = db.session.query(ReviewType).filter(ReviewType.name==func.binary(review_type)).first()
		response = {}

		# get all ratings
		ratings = db.session.query(Question.name, Question.id, func.avg(Rating.point).label('average'))\
							.filter(and_(Rating.object_id==object_id, Rating.question_id.in_(db.session.query(Question.id).filter(Question.type_id==rt.id)))) \
							.filter(Question.id==Rating.question_id) \
							.group_by(Question.name, Question.id) \
							.all()

		rs = []
		for r in ratings:
			data = {
				"id": r.id,
				"name": r.name,
				"average": r.average
			}
			comments = db.session.query(Comment).filter(Comment.rating_id.in_(db.session.query(Rating.id).filter(Rating.question_id==r.id))).limit(5).all()
			tmp = []
			for c in comments:
				cjson = c.to_json()
				cjson['user'] = c.rating.user.to_json()
				tmp.append(cjson)
			data['comments'] = tmp
			rs.append(data)

		response['ratings'] = rs
		response['first_review'] = 1 if len(ratings) == 0 else 0
		response['user'] = user.to_json()

		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)