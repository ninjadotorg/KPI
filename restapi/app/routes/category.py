import os
import json
import app.constants as CONST

from flask import Blueprint, request, current_app as app
from sqlalchemy import and_
from app.helpers.response import response_ok, response_error
from app.helpers.decorators import login_required
from app import db
from app.models import Category
from app.helpers.message import MESSAGE, CODE

category_routes = Blueprint('category', __name__)

@category_routes.route('/', methods=['GET'])
@login_required
def cates():
	try:
		categories = Category.query.all()
		data = []

		for cate in categories:
			data.append(cate.to_json())

		return response_ok(data)
	except Exception, ex:
		return response_error(ex.message)


@category_routes.route('/add', methods=['POST'])
@login_required
def add():
	try:
		uid = int(request.headers['Uid'])
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		cates = []
		response_json = []
		for item in data:
			cate = Category(
				name=item['name'],
				created_user_id=uid
			)
			db.session.add(cate)
			db.session.flush()
			cates.append(cate)

			response_json.append(cate.to_json())

		db.session.commit()
		return response_ok(response_json)
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@category_routes.route('/remove/<int:id>', methods=['POST'])
@login_required
def remove(id):
	try:
		uid = int(request.headers['Uid'])
		cate = db.session.query(Category).filter(and_(Category.id==id, Category.created_user_id==uid)).first()
		if cate is not None:
			db.session.delete(cate)
			db.session.commit()
			return response_ok(message="{} has been deleted!".format(cate.id))
		else:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@category_routes.route('/update/<int:id>', methods=['POST'])
@login_required
def update(id):
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		uid = int(request.headers['Uid'])
		cate = db.session.query(Category).filter(and_(Category.id==id, Category.created_user_id==uid)).first()
		if cate is not None:
			cate.name = data['name']
			db.session.commit()

			return response_ok(message='{} has been updated'.format(cate.id))
		else:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)