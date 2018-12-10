# -*- coding: utf-8 -*-
import os
import sys
import hashlib
import json
import app.bl.user as user_bl
import app.constants as CONST
import app.bl.match as match_bl
import app.bl.admin as admin_bl
import app.bl.contract as contract_bl
import app.bl.storage as storage_bl
import logging

from flask import Blueprint, request, g
from app import db, sg, s3
from datetime import datetime
from sqlalchemy import and_

from app.models import Match, Outcome, Task, Handshake, Shaker, Contract, Source, Token
from app.helpers.utils import local_to_utc
from app.helpers.message import MESSAGE, CODE
from app.helpers.decorators import admin_required, dev_required
from app.helpers.response import response_ok, response_error
from app.constants import Handshake as HandshakeStatus
from flask_jwt_extended import jwt_required
from app.tasks import update_status_feed, upload_file_google_storage, send_email_event_verification_failed


admin_routes = Blueprint('admin', __name__)
logfile = logging.getLogger('file')


@admin_routes.route('/create_market', methods=['POST'])
@admin_required
def create_market():
	"""
	" Admin create new markets
	"	- Based on fixtures.json
	"	- image file should be stored at /files/temp
	"""
	try:
		fixtures_path = os.path.abspath(os.path.dirname(__file__)) + '/fixtures.json'
		data = {}
		with open(fixtures_path, 'r') as f:
			data = json.load(f)

		if 'fixtures' in data:
			fixtures = data['fixtures']
			for item in fixtures:

				contract = contract_bl.get_active_smart_contract()
				if contract is None:
					return response_error(MESSAGE.CONTRACT_EMPTY_VERSION, CODE.CONTRACT_EMPTY_VERSION)

				# check token id
				token_id = item['token_id']
				if token_id is not None:
					token = Token.find_token_by_id(token_id)
					if token is None:
						return response_error(MESSAGE.TOKEN_NOT_FOUND, CODE.TOKEN_NOT_FOUND)
					token_id = token.id

					# refresh erc20 contract
					contract = contract_bl.get_active_smart_contract(contract_type=CONST.CONTRACT_TYPE['ERC20'])
					if contract is None:
						return response_error(MESSAGE.CONTRACT_EMPTY_VERSION, CODE.CONTRACT_EMPTY_VERSION)

				match = Match(
							homeTeamName=item['homeTeamName'],
							awayTeamName=item['awayTeamName'],
							name=item['name'],
							market_fee=int(item.get('market_fee', 0)),
							source_id=int(item['source_id']),
							category_id=int(item['category_id']),
							public=int(item['public']),
							date=item['date'],
							reportTime=item['reportTime'],
							disputeTime=item['disputeTime']
						)
				db.session.add(match)
				db.session.flush()

				for o in item['outcomes']:
					outcome = Outcome(
						name=o.get('name', ''),
						match_id=match.id,
						contract_id=contract.id,
						token_id=token_id,
						approved=CONST.OUTCOME_STATUS['APPROVED']
					)
					db.session.add(outcome)
					db.session.flush()

				# add Task
				task = Task(
					task_type=CONST.TASK_TYPE['REAL_BET'],
					data=json.dumps(match.to_json()),
					action=CONST.TASK_ACTION['CREATE_MARKET'],
					status=-1,
					contract_address=contract.contract_address,
					contract_json=contract.json_name
				)
				db.session.add(task)
				db.session.flush()

				# Handle upload file to Google Storage
				if item['image'] is not None and len(item['image']) > 0:
					upload_file_google_storage.delay(match.id, storage_bl.formalize_filename(os.path.basename(item['image'])), item['image'])

		db.session.commit()
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@admin_routes.route('/review-market/<int:market_id>', methods=['POST'])
@jwt_required
def review_market(market_id):
	"""
	" Admin approve/reject user market.
	"""
	try:
		data = request.json
		outcome_id = data.get("outcome_id", -1)
		status = data.get("status", CONST.OUTCOME_STATUS['APPROVED'])

		match = None
		if outcome_id == -1:
			match = Match.find_match_by_id(market_id)
			if match is not None:
				for o in match.outcomes:
					if o.approved == CONST.OUTCOME_STATUS['PENDING'] and o.hid is None:
						o.approved = status
						db.session.flush()

				if status == CONST.OUTCOME_STATUS['APPROVED']:
					task = admin_bl.add_create_market_task(match)
					if task is not None:				
						db.session.add(task)
						db.session.flush()
					else:
						return response_error(MESSAGE.CONTRACT_EMPTY_VERSION, CODE.CONTRACT_EMPTY_VERSION)
				else:
					send_email_event_verification_failed.delay(match.id, match.created_user_id)

			else:
				return response_error(MESSAGE.MATCH_NOT_FOUND, CODE.MATCH_NOT_FOUND)

		else:
			outcome = db.session.query(Outcome).filter(and_(Outcome.id==outcome_id, Outcome.match_id==market_id)).first()
			if outcome is None:
				return response_error(MESSAGE.OUTCOME_INVALID, CODE.OUTCOME_INVALID)

			if outcome.approved == CONST.OUTCOME_STATUS['PENDING'] and outcome.hid is None:
				outcome.approved = status
				db.session.flush()

				match = outcome.match
				if status == CONST.OUTCOME_STATUS['APPROVED']:
					task = admin_bl.add_create_market_task(match)
					if task is not None:				
						db.session.add(task)
						db.session.flush()
					else:
						return response_error(MESSAGE.CONTRACT_EMPTY_VERSION, CODE.CONTRACT_EMPTY_VERSION)
						
				else:
					send_email_event_verification_failed.delay(match.id, match.created_user_id)

			else:
				return response_error(MESSAGE.MATCH_HAS_BEEN_REVIEWED, CODE.MATCH_HAS_BEEN_REVIEWED)

		db.session.commit()
		return response_ok(match.to_json())
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@admin_routes.route('/init_default_odds', methods=['POST'])
@admin_required
def init_default_odds():
	"""
	"	Admin create odds for market in ETH
	"""
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		for item in data:
			outcome_id = item['outcome_id']
			outcome_data = item['outcomes']
			outcome = Outcome.find_outcome_by_id(outcome_id)
			if outcome is None:
				return response_error(MESSAGE.OUTCOME_INVALID, CODE.OUTCOME_INVALID)

			if outcome.result != CONST.RESULT_TYPE['PENDING']:
				return response_error(MESSAGE.OUTCOME_HAS_RESULT, CODE.OUTCOME_HAS_RESULT)

			match = Match.find_match_by_id(outcome.match_id)
			for o in outcome_data:
				o['outcome_id'] = outcome_id
				o['hid'] = outcome.hid
				o['match_date'] = match.date
				o['match_name'] = match.name
				o['outcome_name'] = outcome.name

				contract = Contract.find_contract_by_id(outcome.contract_id)
				if contract is None:
					return response_error(MESSAGE.CONTRACT_INVALID, CODE.CONTRACT_INVALID)

				task = Task(
					task_type=CONST.TASK_TYPE['REAL_BET'],
					data=json.dumps(o),
					action=CONST.TASK_ACTION['INIT'],
					status=-1,
					contract_address=contract.contract_address,
					contract_json=contract.json_name
				)
				db.session.add(task)
				db.session.flush()
		
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@admin_routes.route('/match/report', methods=['GET'])
@jwt_required
def matches_need_report_by_admin():
	try:
		response = []
		matches = []

		t = datetime.now().timetuple()
		seconds = local_to_utc(t)

		matches_by_admin = db.session.query(Match).filter(\
														Match.date < seconds, \
														Match.reportTime >= seconds, \
														Match.id.in_(db.session.query(Outcome.match_id).filter(and_(\
																													Outcome.result == -1, \
																													Outcome.hid != None))\
																										.group_by(Outcome.match_id))) \
													.order_by(Match.date.asc(), Match.index.desc()).all()

		for match in matches_by_admin:
			match_json = match.to_json()
			arr_outcomes = []
			for outcome in match.outcomes:
				if admin_bl.can_admin_report_this_outcome(outcome):
					arr_outcomes.append(outcome.to_json())

			if len(arr_outcomes) > 0:
				match_json["outcomes"] = arr_outcomes
				response.append(match_json)

		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)


@admin_routes.route('/match/resolve', methods=['GET'])
@jwt_required
def matches_need_resolve_by_admin():
	try:
		response = []
		matches = []

		t = datetime.now().timetuple()
		seconds = local_to_utc(t)

		matches_disputed = db.session.query(Match).filter(Match.id.in_(db.session.query(Outcome.match_id).filter(and_(Outcome.result == CONST.RESULT_TYPE['DISPUTED'], Outcome.hid != None)).group_by(Outcome.match_id))).order_by(Match.date.asc(), Match.index.desc()).all()

		for match in matches_disputed:
			match_json = match.to_json()
			arr_outcomes = []
			for outcome in match.outcomes:
				if outcome.result == CONST.RESULT_TYPE['DISPUTED']:
					outcome_json = outcome.to_json()
					arr_outcomes.append(outcome_json)

			if len(arr_outcomes) > 0:
				match_json["outcomes"] = arr_outcomes if len(arr_outcomes) > 0 else []
				response.append(match_json)

		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)


@admin_routes.route('match/report/<int:match_id>', methods=['POST'])
@jwt_required
def report_match(match_id):
	""" Report match by match_id: 
	"" If report is 'PROCESSING' status, tnx's action is 'REPORT'
	"" If report is 'DISPUTED' status, tnx's action is 'RESOLVE'
	""
	""	Input: 
	""		match_id
	"""
	try:
		t = datetime.now().timetuple()
		seconds = local_to_utc(t)

		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		match = db.session.query(Match).filter(\
											Match.date < seconds,
											Match.id == match_id).first()
		if match is not None:
			result = data['result']
			if result is None:
				return response_error(MESSAGE.MATCH_RESULT_EMPTY)

			disputed = False
			for item in result:
				if 'side' not in item:
					return response_error(MESSAGE.OUTCOME_INVALID_RESULT)

				if 'outcome_id' not in item:
					return response_error(MESSAGE.OUTCOME_INVALID)

				outcome = db.session.query(Outcome).filter(Outcome.id==item['outcome_id'], Outcome.match_id==match.id).first()
				if outcome is not None:
					message, code = match_bl.is_able_to_set_result_for_outcome(outcome)
					if message is not None and code is not None:
						return message, code
					
					if outcome.result == CONST.RESULT_TYPE['DISPUTED']:
						disputed = True

					outcome.result = CONST.RESULT_TYPE['PROCESSING']

				else:
					return response_error(MESSAGE.OUTCOME_INVALID)

				contract = Contract.find_contract_by_id(outcome.contract_id)
				if contract is None:
					return response_error(MESSAGE.CONTRACT_INVALID, CODE.CONTRACT_INVALID)

				report = {}
				report['offchain'] = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + ('resolve' if disputed else 'report') + str(outcome.id) + '_' + str(item['side'])
				report['hid'] = outcome.hid
				report['outcome_id'] = outcome.id
				report['outcome_result'] = item['side']
				report['creator_wallet_address'] = match.creator_wallet_address
				report['grant_permission'] = match.grant_permission

				task = Task(
					task_type=CONST.TASK_TYPE['REAL_BET'],
					data=json.dumps(report),
					action=CONST.TASK_ACTION['RESOLVE' if disputed else 'REPORT'],
					status=-1,
					contract_address=contract.contract_address,
					contract_json=contract.json_name
				)
				db.session.add(task)
				db.session.flush()

			db.session.commit()
			return response_ok(match.to_json())
		else:
			return response_error(MESSAGE.MATCH_NOT_FOUND, CODE.MATCH_NOT_FOUND)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@admin_routes.route('/source/approve/<int:source_id>', methods=['POST'])
@jwt_required
def approve_source(source_id):
	try:
		source = Source.find_source_by_id(source_id)
		if source is not None:
			if source.approved != 1:
				source.approved = 1
				db.session.flush()
			else:
				return response_error(MESSAGE.SOURCE_APPOVED_ALREADY, CODE.SOURCE_APPOVED_ALREADY)
				
		else:
			return response_error(MESSAGE.SOURCE_INVALID, CODE.SOURCE_INVALID)

		db.session.commit()
		return response_ok(source.to_json())
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@admin_routes.route('/update-feed-status', methods=['POST'])
@jwt_required
def update_feed_status():
	try:
		data = request.json
		is_maker = int(data.get('is_maker', -1))
		item_id = int(data.get('id', -1))
		status = int(data.get('status', -1))
		amount = data.get('amount') # string
		remaining_amount = data.get('remaining_amount') # string

		if is_maker == -1 or status == -1 or item_id == -1:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		handshake = None

		if is_maker == 1:
			handshake = Handshake.find_handshake_by_id(item_id)
			if handshake is not None:
				handshake.status = status
				if amount is not None:
					handshake.amount = amount
				if remaining_amount is not None:
					handshake.remaining_amount = remaining_amount
		else:
			shaker = Shaker.find_shaker_by_id(item_id)
			if shaker is not None:
				shaker.status = status
				handshake = Handshake.find_handshake_by_id(shaker.handshake_id)
				if handshake is not None:
					status = handshake.status

					if amount is not None:
						handshake.amount = amount
					if remaining_amount is not None:
						handshake.remaining_amount = remaining_amount

		db.session.flush()
		db.session.commit()
		update_status_feed.delay(handshake.id, status, amount=amount, remaining_amount=remaining_amount)
		return response_ok()

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)