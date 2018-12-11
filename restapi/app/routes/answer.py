# -*- coding: utf-8 -*-
import os
import sys
import hashlib
import json
import app.constants as CONST
import logging

from flask import Blueprint, request, g
from app import db
from datetime import datetime
from sqlalchemy import and_, func

from app.models import Rating
from app.helpers.message import MESSAGE, CODE
from app.helpers.decorators import admin_required, dev_required
from app.helpers.response import response_ok, response_error
from flask_jwt_extended import jwt_required


answer_routes = Blueprint('answer', __name__)
logfile = logging.getLogger('file')


@answer_routes.route('/submit', methods=['POST'])
@jwt_required
def submit_answer():
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)
			
		review_type = request.args.get('type', '')
		object_id = request.args.get('id', -1)
		
		if len(review_type) == 0 or \
			object_id == -1:
			return response_error(MESSAGE.ANSWER_INVALID_INPUT, CODE.ANSWER_INVALID_INPUT)

		ratings = data['ratings']
		if ratings is not None:
			for r in ratings:
				if 'question_id' not in r:
					return response_error(MESSAGE.ANSWER_INVALID_QUESTION_ID, CODE.ANSWER_INVALID_QUESTION_ID)

				r = Rating(
					point=r['rating'],
					question_id=r['question_id'],
					object_id=object_id
				)
				db.session.add(r)
				db.session.flush()

		comment = data['comment']
		if comment is not None:
			pass

		return response_ok()
	except Exception, ex:
		return response_error(ex.message)


@answer_routes.route('/view', methods=['GET'])
@jwt_required
def view_answer():
	try:
		return response_ok()
	except Exception, ex:
		return response_error(ex.message)