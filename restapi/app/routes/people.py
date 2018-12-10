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
from sqlalchemy import and_

from app.helpers.message import MESSAGE, CODE
from app.helpers.decorators import admin_required, dev_required
from app.helpers.response import response_ok, response_error
from flask_jwt_extended import jwt_required


people_routes = Blueprint('people', __name__)
logfile = logging.getLogger('file')


@people_routes.route('/list', methods=['GET'])
@jwt_required
def all_people():
	try:
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@people_routes.route('/view/<int:people_id>', methods=['GET'])
@jwt_required
def view_detail(people_id):
	try:
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)