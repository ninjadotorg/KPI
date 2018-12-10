import os
import json
import app.constants as CONST
import app.bl.referral as referral_bl

from flask import Blueprint, request, g
from app.helpers.response import response_ok, response_error
from app.helpers.decorators import login_required
from app import db
from app.models import Referral, User
from app.helpers.message import MESSAGE, CODE

referral_routes = Blueprint('referral', __name__)

@referral_routes.route('/check', methods=['GET'])
@login_required
def check_referral():
	"""
	" check user has joined referral program or not
	"""
	try:
		uid = int(request.headers['Uid'])
		r = Referral.find_referral_by_uid(uid)

		response = {
			"code": None,
			"referral_link": None,
			"referred_users": referral_bl.all_referred_users_by_user(uid)
		}
		if r is None:
			return response_error(response)

		response['code'] = r.code
		response['referral_link'] = '{}prediction?refer={}'.format(g.BASE_URL, r.code)
		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)


@referral_routes.route('/join', methods=['GET'])
@login_required
def join_referral_program():
	"""
	" user joins referral program
	"""
	try:
		uid = int(request.headers['Uid'])
		if referral_bl.is_user_can_join_referral_program(User.find_user_with_id(uid)):
			r = Referral(
				code=referral_bl.generate_referral_code(uid),
				user_id=uid
			)
			db.session.add(r)
			db.session.commit()

			response = r.to_json()
			response['referral_link'] = '{}prediction?refer={}'.format(g.BASE_URL, r.code)

			return response_ok(response)

		return response_error(MESSAGE.REFERRAL_USER_JOINED_ALREADY, CODE.REFERRAL_USER_JOINED_ALREADY)
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
