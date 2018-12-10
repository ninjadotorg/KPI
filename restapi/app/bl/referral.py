import string
import random

from flask import g
from app import db
from app.models import User, Redeem, Referral
from app.tasks import send_reward_redeem
from app.helpers.utils import is_valid_email


def generate_referral_code(user_id):
	chars = string.ascii_uppercase + string.ascii_lowercase
	code = '{}{}{}'.format(user_id, string_generator(2), string_num_generator(2))
	return code


def issue_referral_code_for_user(user):
	r = Referral.find_referral_by_uid(user.id)
	if r is None:
		code = generate_referral_code(user.id)
		r = Referral(
			code=code,
			user_id=user.id
		)
		db.session.add(r)
		db.session.flush()

	return r.code


def string_generator(size):
	chars = string.ascii_uppercase + string.ascii_lowercase
	return ''.join(random.choice(chars) for _ in range(size))


def string_num_generator(size):
	chars = string.ascii_lowercase + string.digits
	return ''.join(random.choice(chars) for _ in range(size))


def give_redeem_code_for_referred_user(user_id):
	"""
	" Give redeem code for user who invites user_id
	"""
	u = User.find_user_with_id(user_id)
	if u is not None and u.invited_by_user is not None and u.invited_by_user > 0:
		redeem = db.session.query(Redeem).filter(Redeem.reserved_id==0, Redeem.used_user==0).limit(1).first()
		if redeem is not None:
			redeem.reserved_id = u.invited_by_user
			db.session.flush()
			
			# send mail to invited user to inform new redeem code
			reward_user_redeem_code(u.invited_by_user, redeem.code)		


def reward_user_redeem_code(user_id, code):
	u = User.find_user_with_id(user_id)
	if u is not None and is_valid_email(u.email):
		send_reward_redeem.delay(u.email, code, '{}prediction?refer={}'.format(g.BASE_URL, code))


def is_user_can_join_referral_program(user):
	r = Referral.find_referral_by_uid(user.id)
	# we remove is_valid_email(user.email) temporary
	if r is None:
		return True

	return False


def all_referred_users_by_user(user_id):
	if user_id is None:
		return None
	
	response = []
	users = db.session.query(User).filter(User.invited_by_user==user_id).all()
	for u in users:
		data = {}
		data['email'] = u.email
		data['redeemed'] = u.played_bet
		response.append(data)
	return response