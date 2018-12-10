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
from sqlalchemy import and_

from app.helpers.message import MESSAGE, CODE
from app.helpers.decorators import admin_required, dev_required
from app.helpers.response import response_ok, response_error
from flask_jwt_extended import jwt_required


company_routes = Blueprint('company', __name__)
logfile = logging.getLogger('file')


@company_routes.route('/list', methods=['GET'])
@jwt_required
def all_companies():
	try:
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
