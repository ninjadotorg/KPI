#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import json

import app.constants as CONST

from flask import g
from app import db
from sqlalchemy import and_, or_, func, text, not_

from app.models import User, Handshake, Match, Outcome, Contract, Shaker
from app.helpers.bc_exception import BcException


def count_users_play_on_outcome(outcome_id):
	users = db.session.query(User)\
			.filter(User.id.in_(db.session.query(Handshake.user_id)\
								.filter(Handshake.outcome_id==outcome_id, Handshake.status!=-1)) |\
					User.id.in_(db.session.query(Shaker.shaker_id)\
							.filter(Shaker.status!=-1, Shaker.handshake_id.in_(db.session.query(Handshake.id)\
																			.filter(Handshake.outcome_id==outcome_id)))))\
			.group_by(User.id).all()
	return len(users)


def count_support_users_play_on_outcome(outcome_id):
	users = db.session.query(User)\
			.filter(User.id.in_(db.session.query(Handshake.user_id)\
								.filter(Handshake.side==CONST.SIDE_TYPE['SUPPORT'], Handshake.outcome_id==outcome_id, Handshake.status!=-1)) |\
					User.id.in_(db.session.query(Shaker.shaker_id)\
							.filter(Shaker.side==CONST.SIDE_TYPE['SUPPORT'], Shaker.status!=-1, Shaker.handshake_id.in_(db.session.query(Handshake.id)\
																			.filter(Handshake.outcome_id==outcome_id)))))\
			.group_by(User.id).all()
	return len(users)


def count_against_users_play_on_outcome(outcome_id):
	users = db.session.query(User)\
			.filter(User.id.in_(db.session.query(Handshake.user_id)\
								.filter(Handshake.side==CONST.SIDE_TYPE['OPPOSE'], Handshake.outcome_id==outcome_id, Handshake.status!=-1)) |\
					User.id.in_(db.session.query(Shaker.shaker_id)\
							.filter(Shaker.side==CONST.SIDE_TYPE['OPPOSE'], Shaker.status!=-1, Shaker.handshake_id.in_(db.session.query(Handshake.id)\
																			.filter(Handshake.outcome_id==outcome_id)))))\
			.group_by(User.id).all()
	return len(users)


def has_result(outcome):
	if outcome is not None and \
		outcome.result is not None and \
		outcome.result in [1, 2, 3]:
		return True

	return False


def check_outcome_valid(outcomes):
	arr_outcomes = []
	for outcome in outcomes:
		if outcome.hid is not None and outcome.approved == CONST.OUTCOME_STATUS['APPROVED']:
			arr_outcomes.append(outcome.to_json())
	return arr_outcomes


def is_outcome_created_by_user(outcome):
	if outcome is not None:
		if outcome.created_user_id is not None and outcome.created_user_id > 0:
			return True

	return False
