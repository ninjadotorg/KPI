# -*- coding: utf-8 -*-
from __future__ import division
import base64
import time
import os
import sys
import simplejson as json
import logging

import app.constants as CONST
import app.bl.handshake as handshake_bl
import app.bl.match as match_bl
import app.bl.user as user_bl
import app.bl.outcome as outcome_bl

from decimal import *
from flask import Blueprint, request, g
from sqlalchemy import or_, and_, text, func

from app.helpers.response import response_ok, response_error
from app.helpers.message import MESSAGE, CODE
from app.helpers.bc_exception import BcException
from app.helpers.decorators import login_required, whitelist
from app.helpers.utils import is_equal, local_to_utc
from app import db
from app.models import User, Handshake, Shaker, Outcome, Match, Task, Contract, Setting, Token, Redeem, History
from app.constants import Handshake as HandshakeStatus
from app.tasks import update_feed, subscribe_email_to_claim_redeem_code
from datetime import *


handshake_routes = Blueprint('handshake', __name__)
getcontext().prec = 18
logfile = logging.getLogger('file')

@handshake_routes.route('/', methods=['POST'])
@login_required
def handshakes():
	uid = int(request.headers['Uid'])
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		outcome_id = data.get('outcome_id', -1)
		outcome = Outcome.find_outcome_by_id(outcome_id)
		if outcome is None:
			return response_error(MESSAGE.INVALID_BET, CODE.INVALID_BET)
		
		match = Match.find_match_by_id(outcome.match_id)
		supports = handshake_bl.find_available_support_handshakes(outcome_id)
		againsts = handshake_bl.find_available_against_handshakes(outcome_id)

		total = Decimal('0', 2)

		traded_volumns = db.session.query(func.sum(Handshake.amount*Handshake.odds).label('traded_volumn')).filter(and_(Handshake.outcome_id==outcome_id, Handshake.status==CONST.Handshake['STATUS_INITED'])).group_by(Handshake.odds).all()
		for traded in traded_volumns:
			total += traded[0]

		arr_supports = []
		for support in supports:
			data = {}
			data['odds'] = support.odds
			data['amount'] = support.amount
			arr_supports.append(data)

		arr_against = []
		for against in againsts:
			data = {}
			data['odds'] = against.odds
			data['amount'] = against.amount
			arr_against.append(data)

		response = {
			"support": arr_supports,
			"against": arr_against,
			"traded_volumn": total,
			"market_fee": match.market_fee
		}

		return response_ok(response)

	except Exception, ex:
		return response_error(ex.message)
	
	return response_ok()


@handshake_routes.route('/<int:id>')
@login_required
def detail(id):
	uid = int(request.headers['Uid'])
	chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
	user = User.find_user_with_id(uid)		

	try:
		handshake = db.session.query(Handshake).filter(and_(Handshake.id==id, Handshake.user_id==uid)).first()
		if handshake is not None:
			return response_ok(handshake.to_json())

		return response_error(MESSAGE.HANDSHAKE_NOT_FOUND, CODE.HANDSHAKE_NOT_FOUND)

	except Exception, ex:
		return response_error(ex.message)


@handshake_routes.route('/init', methods=['POST'])
@login_required
def init():
	"""
	" User plays bet in binary event.
	"""
	try:
		from_request = request.headers.get('Request-From', 'mobile')
		uid = int(request.headers['Uid'])
		chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		user = User.find_user_with_id(uid)		

		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		hs_type = data.get('type', -1)
		extra_data = data.get('extra_data', '')
		description = data.get('description', '')
		outcome_id = data.get('outcome_id', -1)
		match_id = data.get('match_id', -1)
		odds = Decimal(data.get('odds', '2')).quantize(Decimal('.1'), rounding=ROUND_HALF_DOWN)
		amount = Decimal(data.get('amount'))
		currency = data.get('currency', 'ETH')
		side = int(data.get('side', CONST.SIDE_TYPE['SUPPORT']))
		chain_id = int(data.get('chain_id', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		from_address = data.get('from_address', '')
		free_bet = data.get('free_bet', 0)

		if hs_type != CONST.Handshake['INDUSTRIES_BETTING']:
			return response_error(MESSAGE.HANDSHAKE_INVALID_BETTING_TYPE, CODE.HANDSHAKE_INVALID_BETTING_TYPE)

		if len(from_address) == 0:
			return response_error(MESSAGE.INVALID_ADDRESS, CODE.INVALID_ADDRESS)

		# check valid outcome or not
		outcome = None
		if match_id == -1:
			outcome = Outcome.find_outcome_by_id(outcome_id)
		else:
			match = Match.find_match_by_id(match_id)
			if match is not None and len(match.outcomes.all()) > 0:
				outcome = match.outcomes[0]

		if outcome is None:
			return response_error(MESSAGE.OUTCOME_INVALID, CODE.OUTCOME_INVALID)

		if outcome.result != CONST.RESULT_TYPE['PENDING']:
			return response_error(MESSAGE.OUTCOME_HAS_RESULT, CODE.OUTCOME_HAS_RESULT)

		outcome_id = outcome.id

		# make sure user cannot call free-bet in ERC20
		if free_bet == 1:
			token = Token.find_token_by_id(outcome.token_id)
			if token is not None:
				return response_error(MESSAGE.HANDSHAKE_CANNOT_CREATE_FREEBET_IN_ERC20, CODE.HANDSHAKE_CANNOT_CREATE_FREEBET_IN_ERC20)

		if odds <= 1:
			return response_error(MESSAGE.INVALID_ODDS, CODE.INVALID_ODDS)

		contract = Contract.find_contract_by_id(outcome.contract_id)
		if contract is None:
			return response_error(MESSAGE.CONTRACT_INVALID, CODE.CONTRACT_INVALID)

		# add to history
		history = History(			
			chain_id=chain_id,
			description=description,
			free_bet=free_bet,
			from_address=from_address,
			contract_address=contract.contract_address,
			contract_json=contract.json_name,
			odds=odds,
			amount=amount,
			currency=currency,
			from_request=from_request,
			side=side,
			user_id=uid,
			outcome_id=outcome_id
		)
		db.session.add(history)
		db.session.flush()

		# filter all handshakes which able be to match first
		handshakes = handshake_bl.find_all_matched_handshakes(side, odds, outcome_id, amount, uid)
		arr_hs = []
		if len(handshakes) == 0:
			handshake = Handshake(
				hs_type=hs_type,
				extra_data=extra_data,
				description=description,
				chain_id=chain_id,
				user_id=user.id,
				outcome_id=outcome_id,
				odds=odds,
				amount=amount,
				currency=currency,
				side=side,
				remaining_amount=amount,
				from_address=from_address,
				free_bet=free_bet,
				contract_address=contract.contract_address,
				contract_json=contract.json_name,
				from_request=from_request,
				history_id=history.id
			)

			db.session.add(handshake)
			db.session.commit()

			update_feed.delay(handshake.id)

			# response data
			hs_json = handshake.to_json()
			hs_json['maker_address'] = handshake.from_address
			hs_json['maker_odds'] = handshake.odds
			hs_json['hid'] = outcome.hid
			hs_json['type'] = 'init'
			hs_json['offchain'] = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + 'm' + str(handshake.id)
			arr_hs.append(hs_json)

			logfile.debug("Uid -> {}, json --> {}".format(uid, arr_hs))
		else:
			shaker_amount = amount

			hs_feed = []
			sk_feed = []
			for handshake in handshakes:
				if shaker_amount.quantize(Decimal('.00000000000000001'), rounding=ROUND_DOWN) <= 0:
					break

				handshake.shake_count += 1
				handshake_win_value = handshake.remaining_amount*handshake.odds
				shaker_win_value = shaker_amount*odds
				subtracted_amount_for_shaker = 0
				subtracted_amount_for_handshake = 0


				if is_equal(handshake_win_value, shaker_win_value):
					subtracted_amount_for_shaker = shaker_amount
					subtracted_amount_for_handshake = handshake.remaining_amount

				elif handshake_win_value >= shaker_win_value:
					subtracted_amount_for_shaker = shaker_amount
					subtracted_amount_for_handshake = shaker_win_value - subtracted_amount_for_shaker

				else:
					subtracted_amount_for_handshake = handshake.remaining_amount
					subtracted_amount_for_shaker = handshake_win_value - subtracted_amount_for_handshake

				handshake.remaining_amount -= subtracted_amount_for_handshake
				shaker_amount -= subtracted_amount_for_shaker
				db.session.merge(handshake)

				o = Outcome.find_outcome_by_id(handshake.outcome_id)

				if o is None:
					return response_error(MESSAGE.OUTCOME_INVALID, CODE.OUTCOME_INVALID)

				c = Contract.find_contract_by_id(o.contract_id)
				if c is None:
					return response_error(MESSAGE.CONTRACT_INVALID, CODE.CONTRACT_INVALID)

				# create shaker
				shaker = Shaker(
					shaker_id=user.id,
					amount=subtracted_amount_for_shaker,
					currency=currency,
					odds=odds,
					side=side,
					handshake_id=handshake.id,
					from_address=from_address,
					chain_id=chain_id,
					free_bet=free_bet,
					contract_address=c.contract_address,
					contract_json=c.json_name,
					from_request=from_request,
					history_id=history.id
				)

				db.session.add(shaker)
				db.session.flush()
				sk_feed.append(shaker)
				
				shaker_json = shaker.to_json()
				shaker_json['maker_address'] = handshake.from_address
				shaker_json['maker_odds'] = handshake.odds
				shaker_json['hid'] = outcome.hid
				shaker_json['type'] = 'shake'
				shaker_json['offchain'] = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + 's' + str(shaker.id)
				arr_hs.append(shaker_json)

			if shaker_amount.quantize(Decimal('.00000000000000001'), rounding=ROUND_DOWN) > Decimal(CONST.CRYPTOSIGN_MINIMUM_MONEY):
				handshake = Handshake(
					hs_type=hs_type,
					extra_data=extra_data,
					description=description,
					chain_id=chain_id,
					user_id=user.id,
					outcome_id=outcome_id,
					odds=odds,
					amount=shaker_amount,
					currency=currency,
					side=side,
					remaining_amount=shaker_amount,
					from_address=from_address,
					free_bet=free_bet,
					contract_address=contract.contract_address,
					contract_json=contract.json_name,
					from_request=from_request,
					history_id=history.id
				)
				db.session.add(handshake)
				db.session.flush()
				hs_feed.append(handshake)			

				hs_json = handshake.to_json()
				hs_json['maker_address'] = handshake.from_address
				hs_json['maker_odds'] = handshake.odds
				hs_json['hid'] = outcome.hid
				hs_json['type'] = 'init'
				hs_json['offchain'] = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + 'm' + str(handshake.id)
				arr_hs.append(hs_json)
			
			db.session.commit()
			logfile.debug("Uid -> {}, json --> {}".format(uid, arr_hs))

			handshake_bl.update_handshakes_feed(hs_feed, sk_feed)

		# make response
		response = {
			"handshakes": arr_hs,
			"total_bets": handshake_bl.get_total_real_bets()
		}
		return response_ok(response)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@handshake_routes.route('/rollback', methods=['POST'])
@login_required
def rollback():
	# rollback init (real, free): DONE
	# rollback shake (real, free): DONE
	try:
		uid = int(request.headers['Uid'])
		chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		user = User.find_user_with_id(uid)

		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		offchain = data.get('offchain')
		if offchain is None or len(offchain) == 0:
			return response_error(MESSAGE.MISSING_OFFCHAIN, CODE.MISSING_OFFCHAIN)

		offchain = offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')
		
		handshakes = []
		shakers = []
		response = None

		if 'm' in offchain:
			offchain = int(offchain.replace('m', ''))
			handshake = db.session.query(Handshake).filter(and_(Handshake.id==offchain, Handshake.user_id==uid)).first()
			if handshake is not None:	
				if handshake_bl.is_init_pending_status(handshake): # rollback maker init state
					handshake.status = HandshakeStatus['STATUS_MAKER_INIT_ROLLBACK']
					db.session.flush()
					handshakes.append(handshake)

				else:
					return response_error(MESSAGE.CANNOT_ROLLBACK, CODE.CANNOT_ROLLBACK)

				response = handshake.to_json()

			else:
				return response_error(MESSAGE.HANDSHAKE_EMPTY, CODE.HANDSHAKE_EMPTY)

		else:
			offchain = int(offchain.replace('s', ''))
			shaker = db.session.query(Shaker).filter(and_(Shaker.id==offchain, Shaker.shaker_id==uid)).first()

			if shaker is not None:
				if shaker.status == HandshakeStatus['STATUS_PENDING']:
					shaker = handshake_bl.rollback_shake_state(shaker)
					shakers.append(shaker)

				else:
					return response_error(MESSAGE.CANNOT_ROLLBACK, CODE.CANNOT_ROLLBACK)

				response = shaker.to_json()

			else:
				return response_error(MESSAGE.SHAKER_NOT_FOUND, CODE.SHAKER_NOT_FOUND)

		db.session.commit()
		handshake_bl.update_handshakes_feed(handshakes, shakers)

		return response_ok(response)
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@handshake_routes.route('/create_free_bet', methods=['POST'])
@login_required
@whitelist
def create_free_bet():
	"""
	"	Create a free-bet in ETH
	"""
	try:
		uid = int(request.headers['Uid'])
		chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		user = User.find_user_with_id(uid)

		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		redeem = data.get('redeem', '')
		match_id = data.get('match_id', -1)
		odds = Decimal(data.get('odds', Decimal('2')))
		amount = Decimal(CONST.CRYPTOSIGN_FREE_BET_AMOUNT)
		side = int(data.get('side', CONST.SIDE_TYPE['SUPPORT']))

		# check valid redeem or not
		r = Redeem.find_redeem_by_code_and_user(redeem, uid)
		if r is None:
			return response_error(MESSAGE.REDEEM_NOT_FOUND, CODE.REDEEM_NOT_FOUND)
		else:
			if r.used_user > 0:
				return response_error(MESSAGE.REDEEM_INVALID, CODE.REDEEM_INVALID)
			r.used_user = uid
			db.session.flush()

		outcome_id = data.get('outcome_id')
		outcome = None
		if match_id == -1:
			outcome = Outcome.find_outcome_by_id(outcome_id)
			if outcome is None:
				return response_error(MESSAGE.OUTCOME_INVALID, CODE.OUTCOME_INVALID)
			elif outcome.result != -1:
				return response_error(MESSAGE.OUTCOME_HAS_RESULT, CODE.OUTCOME_HAS_RESULT)

		else:
			match = Match.find_match_by_id(match_id)
			if match is not None and len(match.outcomes.all()) > 0:
				outcome = match.outcomes[0]
			else:
				return response_error(MESSAGE.MATCH_NOT_FOUND, CODE.MATCH_NOT_FOUND)

		# check erc20 token or not
		token = Token.find_token_by_id(outcome.token_id)
		if token is not None:
			return response_error(MESSAGE.HANDSHAKE_CANNOT_CREATE_FREEBET_IN_ERC20, CODE.HANDSHAKE_CANNOT_CREATE_FREEBET_IN_ERC20)

		contract = Contract.find_contract_by_id(outcome.contract_id)
		if contract is None:
			return response_error(MESSAGE.CONTRACT_INVALID, CODE.CONTRACT_INVALID)

		match = Match.find_match_by_id(outcome.match_id)
		data['hid'] = outcome.hid
		data['outcome_name'] = outcome.name
		data['match_date'] = match.date
		data['match_name'] = match.name
		data['uid'] = uid
		data['payload'] = user.payload
		data['free_bet'] = 1
		data['amount'] = CONST.CRYPTOSIGN_FREE_BET_AMOUNT

		user.free_bet += 1
		task = Task(
			task_type=CONST.TASK_TYPE['FREE_BET'],
			data=json.dumps(data),
			action=CONST.TASK_ACTION['INIT'],
			status=-1,
			contract_address=contract.contract_address,
			contract_json=contract.json_name
		)
		db.session.add(task)
		db.session.commit()

		# this is for frontend
		handshakes = handshake_bl.find_all_matched_handshakes(side, odds, outcome.id, amount, uid)
		response = {}
		if len(handshakes) == 0:
			response['match'] = 0
		else:
			response['match'] = 1
		return response_ok(response)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@handshake_routes.route('/uninit_free_bet/<int:handshake_id>', methods=['POST'])
@login_required
def uninit_free_bet(handshake_id):
	"""
	"	Uninit free-bet in ETH
	"""
	try:
		uid = int(request.headers['Uid'])
		chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		user = User.find_user_with_id(uid)

		handshake = db.session.query(Handshake).filter(and_(Handshake.id==handshake_id, Handshake.chain_id==chain_id, Handshake.user_id==uid, Handshake.free_bet==1)).first()
		if handshake is not None and \
			(handshake.status == CONST.Handshake['STATUS_INITED'] or \
			handshake.status == CONST.Handshake['STATUS_MAKER_SHOULD_UNINIT']):

			if handshake_bl.can_uninit(handshake) == False:
				return response_error(MESSAGE.HANDSHAKE_CANNOT_UNINIT, CODE.HANDSHAKE_CANNOT_UNINIT)
			else:

				outcome = Outcome.find_outcome_by_id(handshake.outcome_id)
				if outcome is None:
					return response_error(MESSAGE.OUTCOME_INVALID, CODE.OUTCOME_INVALID)
				else:
					# check erc20 token or not
					token = Token.find_token_by_id(outcome.token_id)
					if token is not None:
						return response_error(MESSAGE.HANDSHAKE_CANNOT_UNINIT_FREE_BET_IN_ERC20, CODE.HANDSHAKE_CANNOT_UNINIT_FREE_BET_IN_ERC20)

					contract = Contract.find_contract_by_id(outcome.contract_id)
					if contract is None:
						return response_error(MESSAGE.CONTRACT_INVALID, CODE.CONTRACT_INVALID)

					handshake.status = CONST.Handshake['STATUS_MAKER_UNINIT_PENDING']
					db.session.flush()
					
					data = {
						'hid': outcome.hid,
						'side': handshake.side,
						'odds': handshake.odds,
						'maker': handshake.from_address,
						'value': handshake.amount,
						'offchain': CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + 'm{}'.format(handshake.id),
						'uid': uid,
						'payload': user.payload,
						'free_bet': 1
					}

					task = Task(
						task_type=CONST.TASK_TYPE['FREE_BET'],
						data=json.dumps(data, use_decimal=True),
						action=CONST.TASK_ACTION['UNINIT'],
						status=-1,
						contract_address=contract.contract_address,
						contract_json=contract.json_name
					)
					db.session.add(task)
					db.session.commit()

					update_feed.delay(handshake.id)
					return response_ok(handshake.to_json())
					
		else:
			return response_error(MESSAGE.HANDSHAKE_NOT_FOUND, CODE.HANDSHAKE_NOT_FOUND)	


	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@handshake_routes.route('/collect_free_bet', methods=['POST'])
@login_required
def collect_free_bet():
	"""
	"	Collect free-bet in ETH
	"""
	try:
		uid = int(request.headers['Uid'])
		chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		user = User.find_user_with_id(uid)

		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		offchain = data.get('offchain', '')
		if len(offchain) == 0:
			return response_error(MESSAGE.MISSING_OFFCHAIN, CODE.MISSING_OFFCHAIN)

		h = []
		s = []
		offchain = offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')
		if 's' in offchain:
			offchain = int(offchain.replace('s', ''))
			shaker = db.session.query(Shaker).filter(and_(Shaker.id==offchain, Shaker.shaker_id==user.id)).first()
			msg = handshake_bl.can_withdraw(handshake=None, shaker=shaker)
			if len(msg) != 0:
				return response_error(msg, CODE.CANNOT_WITHDRAW)
			
			hs = Handshake.find_handshake_by_id(shaker.handshake_id)
			outcome = Outcome.find_outcome_by_id(hs.outcome_id)

			# check erc20 token or not
			token = Token.find_token_by_id(outcome.token_id)
			if token is not None:
				return response_error(MESSAGE.HANDSHAKE_CANNOT_WITHDRAW_FREEBET_IN_ERC20, CODE.HANDSHAKE_CANNOT_WITHDRAW_FREEBET_IN_ERC20)

			h = db.session.query(Handshake).filter(and_(Handshake.user_id==user.id, Handshake.outcome_id==hs.outcome_id, Handshake.side==shaker.side, Handshake.status==HandshakeStatus['STATUS_INITED'])).all()
			s = db.session.query(Shaker).filter(and_(Shaker.shaker_id==user.id, Shaker.side==shaker.side, Shaker.status==HandshakeStatus['STATUS_SHAKER_SHAKED'], Shaker.handshake_id.in_(db.session.query(Handshake.id).filter(Handshake.outcome_id==hs.outcome_id)))).all()

			data['hid'] = outcome.hid
			data['winner'] = shaker.from_address

		else:
			offchain = int(offchain.replace('m', ''))
			handshake = db.session.query(Handshake).filter(and_(Handshake.id==offchain, Handshake.user_id==user.id)).first()
			msg = handshake_bl.can_withdraw(handshake)
			if len(msg) != 0:
				return response_error(msg, CODE.CANNOT_WITHDRAW)

			outcome = Outcome.find_outcome_by_id(handshake.outcome_id)

			# check erc20 token or not
			token = Token.find_token_by_id(outcome.token_id)
			if token is not None:
				return response_error(MESSAGE.HANDSHAKE_CANNOT_WITHDRAW_FREEBET_IN_ERC20, CODE.HANDSHAKE_CANNOT_WITHDRAW_FREEBET_IN_ERC20)

			h = db.session.query(Handshake).filter(and_(Handshake.user_id==user.id, Handshake.outcome_id==handshake.outcome_id, Handshake.side==handshake.side, Handshake.status==HandshakeStatus['STATUS_INITED'])).all()
			s = db.session.query(Shaker).filter(and_(Shaker.shaker_id==user.id, Shaker.side==handshake.side, Shaker.status==HandshakeStatus['STATUS_SHAKER_SHAKED'], Shaker.handshake_id.in_(db.session.query(Handshake.id).filter(Handshake.outcome_id==handshake.outcome_id)))).all()

			data['hid'] = outcome.hid
			data['winner'] = handshake.from_address


		handshakes = []
		shakers = []
		response = {}
		# update status
		for hs in h:
			hs.status = HandshakeStatus['STATUS_COLLECT_PENDING']
			db.session.flush()
			handshakes.append(hs)

			if hs.id == offchain:
				response = hs.to_json()
			
		for sk in s:
			sk.status = HandshakeStatus['STATUS_COLLECT_PENDING']
			db.session.flush()
			shakers.append(sk)

			if sk.id == offchain:
				response = sk.to_json()

		data['uid'] = uid
		data['payload'] = user.payload
		data['free_bet'] = 1

		contract = Contract.find_contract_by_id(outcome.contract_id)
		if contract is None:
			return response_error(MESSAGE.CONTRACT_INVALID, CODE.CONTRACT_INVALID)

		# add task
		task = Task(
			task_type=CONST.TASK_TYPE['FREE_BET'],
			data=json.dumps(data),
			action=CONST.TASK_ACTION['COLLECT'],
			status=-1,
			contract_address=contract.contract_address,
			contract_json=contract.json_name
		)
		db.session.add(task)
		db.session.commit()

		handshake_bl.update_handshakes_feed(handshakes, shakers)
		return response_ok(response)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@handshake_routes.route('/refund_free_bet', methods=['POST'])
@login_required
def refund_free_bet():
	"""
	"	Refund free-bet in ETH
	"""
	try:
		uid = int(request.headers['Uid'])
		chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		user = User.find_user_with_id(uid)

		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		offchain = data.get('offchain', '')
		if len(offchain) == 0:
			return response_error(MESSAGE.MISSING_OFFCHAIN, CODE.MISSING_OFFCHAIN)

		handshakes = []
		shakers = []

		offchain = offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')
		if 's' in offchain:
			offchain = int(offchain.replace('s', ''))
			shaker = db.session.query(Shaker).filter(and_(Shaker.id==offchain, Shaker.shaker_id==user.id)).first()
			if handshake_bl.can_refund(None, shaker=shaker):
				shaker.bk_status = shaker.status
				shaker.status = HandshakeStatus['STATUS_REFUNDED']
				db.session.merge(shaker)
				db.session.flush()
				shakers.append(shaker)

			else:
				return response_error(MESSAGE.HANDSHAKE_CANNOT_REFUND, CODE.HANDSHAKE_CANNOT_REFUND)

		elif 'm' in offchain:
			offchain = int(offchain.replace('m', ''))
			handshake = db.session.query(Handshake).filter(and_(Handshake.id==offchain, Handshake.user_id==user.id)).first()
			if handshake_bl.can_refund(handshake):
				handshake.bk_status = handshake.status
				handshake.status = HandshakeStatus['STATUS_REFUNDED']
				db.session.merge(handshake)
				db.session.flush()
				handshakes.append(handshake)

			else:
				return response_error(MESSAGE.HANDSHAKE_CANNOT_REFUND, CODE.HANDSHAKE_CANNOT_REFUND)
			
		else:
			return response_error(MESSAGE.HANDSHAKE_NOT_FOUND, CODE.HANDSHAKE_NOT_FOUND)	

		db.session.commit()

		# update feed
		handshake_bl.update_handshakes_feed(handshakes, shakers)
		
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@handshake_routes.route('/check_redeem_code', methods=['GET'])
@login_required
def check_redeem_code():
	"""
	" At the first time, check user be able to use redeem or not
	"""
	try:
		uid = int(request.headers['Uid'])
		user = User.find_user_with_id(uid)

		# check user be able to claim redeem code or not
		result = user_bl.is_able_to_claim_redeem_code(user)

		is_subscribe = 1 if user.email is not None and len(user.email) > 0 and user.is_subscribe == 1 else 0
		if user_bl.is_user_subscribed_but_still_not_receive_redeem_code(user, result):
			# claim redeem code
			result, code_1, code_2 = user_bl.claim_redeem_code_for_user(user)
			if result:
				subscribe_email_to_claim_redeem_code.delay(user.email, code_1, code_2, request.headers["Fcm-Token"], request.headers["Payload"], uid)

		# check user be able to use redeem code or not
		if result == False:
			# gift to producthunt user
			gift = db.session.query(Redeem).filter(Redeem.reserved_id==user.id, Redeem.code==func.binary('DOJO')).first()
			if gift is None:
				r = Redeem(
					code='DOJO',
					reserved_id=user.id
				)
				db.session.add(r)
				db.session.flush()
				result = True
			
		if result == False:
			result = user_bl.is_able_to_use_redeem_code(user)

		response = {
			"is_user_disable_popup": user.is_user_disable_popup,
			"is_subscribe": is_subscribe,
			"amount": CONST.CRYPTOSIGN_FREE_BET_AMOUNT,
			"redeem": int(result)
		}

		db.session.commit()
		return response_ok(response)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@handshake_routes.route('/uninit', methods=['POST'])
@login_required
def uninit():
	"""
	"	Uninit real bet:
	"		This step make sure user's feed will update pending status
	"""
	try:
		uid = int(request.headers['Uid'])
		user = User.find_user_with_id(uid)

		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		offchain = data.get('offchain', '')
		if len(offchain) == 0:
			return response_error(MESSAGE.MISSING_OFFCHAIN, CODE.MISSING_OFFCHAIN)

		handshakes = []
		shakers = []

		offchain = offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')
		if 'm' in offchain:
			offchain = int(offchain.replace('m', ''))
			handshake = db.session.query(Handshake).filter(and_(Handshake.id==offchain, Handshake.user_id==user.id)).first()
			if handshake_bl.can_uninit(handshake):
				handshake.bk_status = handshake.status
				handshake.status = HandshakeStatus['STATUS_MAKER_UNINIT_PENDING']
				db.session.flush()
				handshakes.append(handshake)
			else:
				return response_error(MESSAGE.HANDSHAKE_CANNOT_UNINIT, CODE.HANDSHAKE_CANNOT_UNINIT)		

		else:
			return response_error(MESSAGE.HANDSHAKE_NOT_FOUND, CODE.HANDSHAKE_NOT_FOUND)	

		db.session.commit()
		handshake_bl.update_handshakes_feed(handshakes, shakers)

		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@handshake_routes.route('/collect', methods=['POST'])
@login_required
def withdraw():
	"""
	"	Collect real bet:
	"		This step make sure user's feed will update pending status
	"""
	try:
		uid = int(request.headers['Uid'])
		user = User.find_user_with_id(uid)

		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		offchain = data.get('offchain', '')
		if len(offchain) == 0:
			return response_error(MESSAGE.MISSING_OFFCHAIN, CODE.MISSING_OFFCHAIN)

		offchain = offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')
		outcome = None
		if 'm' in offchain:
			offchain = int(offchain.replace('m', ''))
			handshake = db.session.query(Handshake).filter(and_(Handshake.id==offchain, Handshake.user_id==user.id)).first()
			if handshake is None:
				return response_error(msg, CODE.CANNOT_WITHDRAW)

			outcome = Outcome.find_outcome_by_id(handshake.outcome_id)

		elif 's' in offchain:
			offchain = int(offchain.replace('s', ''))
			shaker = db.session.query(Shaker).filter(and_(Shaker.id==offchain, Shaker.shaker_id==user.id)).first()
			if shaker is None:
				return response_error(msg, CODE.CANNOT_WITHDRAW)

			handshake = Handshake.find_handshake_by_id(shaker.handshake_id)
			outcome = Outcome.find_outcome_by_id(handshake.outcome_id)

		if outcome is None:
			return response_error(MESSAGE.OUTCOME_INVALID, CODE.OUTCOME_INVALID)

		handshakes = db.session.query(Handshake).filter(and_(Handshake.status.in_([HandshakeStatus['STATUS_INITED'], HandshakeStatus['STATUS_RESOLVED']]), Handshake.user_id==user.id, Handshake.outcome_id==outcome.id, Handshake.side==outcome.result)).all()
		shakers = db.session.query(Shaker).filter(and_(Shaker.status.in_([HandshakeStatus['STATUS_SHAKER_SHAKED'], HandshakeStatus['STATUS_RESOLVED']]), Shaker.shaker_id==user.id, Shaker.side==outcome.result, Shaker.handshake_id.in_(db.session.query(Handshake.id).filter(Handshake.outcome_id==outcome.id)))).all()

		for h in handshakes:
			h.bk_status = h.status
			h.status = HandshakeStatus['STATUS_COLLECT_PENDING']
			db.session.merge(h)

		for s in shakers:
			s.bk_status = s.status
			s.status = HandshakeStatus['STATUS_COLLECT_PENDING']
			db.session.merge(s)
			
		db.session.commit()
		handshake_bl.update_handshakes_feed(handshakes, shakers)

		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@handshake_routes.route('/refund', methods=['POST'])
@login_required
def refund():
	"""
	"	Refund real bet:
	"		This step make sure user's feed will update pending status
	"""
	try:
		uid = int(request.headers['Uid'])
		user = User.find_user_with_id(uid)

		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		offchain = data.get('offchain', '')
		if len(offchain) == 0:
			return response_error(MESSAGE.MISSING_OFFCHAIN, CODE.MISSING_OFFCHAIN)

		offchain = offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')
		outcome = None
		if 'm' in offchain:
			offchain = int(offchain.replace('m', ''))
			handshake = db.session.query(Handshake).filter(and_(Handshake.id==offchain, Handshake.user_id==user.id)).first()
			if handshake is None:
				return response_error(MESSAGE.HANDSHAKE_CANNOT_REFUND, CODE.HANDSHAKE_CANNOT_REFUND)

			outcome = Outcome.find_outcome_by_id(handshake.outcome_id)

		elif 's' in offchain:
			offchain = int(offchain.replace('s', ''))
			shaker = db.session.query(Shaker).filter(and_(Shaker.id==offchain, Shaker.shaker_id==user.id)).first()
			if shaker is None:
				return response_error(MESSAGE.HANDSHAKE_CANNOT_REFUND, CODE.HANDSHAKE_CANNOT_REFUND)

			handshake = Handshake.find_handshake_by_id(shaker.handshake_id)
			outcome = Outcome.find_outcome_by_id(handshake.outcome_id)


		if outcome is None:
			return response_error(MESSAGE.OUTCOME_INVALID, CODE.OUTCOME_INVALID)

		handshakes = db.session.query(Handshake).filter(and_(Handshake.status.in_([HandshakeStatus['STATUS_INITED'], HandshakeStatus['STATUS_RESOLVED']]), Handshake.user_id==user.id, Handshake.outcome_id==outcome.id)).all()
		shakers = db.session.query(Shaker).filter(and_(Shaker.status.in_([HandshakeStatus['STATUS_SHAKER_SHAKED'], HandshakeStatus['STATUS_RESOLVED']]), Shaker.shaker_id==user.id, Shaker.handshake_id.in_(db.session.query(Handshake.id).filter(Handshake.outcome_id==outcome.id)))).all()

		for h in handshakes:
			h.bk_status = h.status
			h.status = HandshakeStatus['STATUS_REFUND_PENDING']
			db.session.merge(h)

		for s in shakers:
			s.bk_status = s.status
			s.status = HandshakeStatus['STATUS_REFUND_PENDING']
			db.session.merge(s)
			
		db.session.commit()
		handshake_bl.update_handshakes_feed(handshakes, shakers)

		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@handshake_routes.route('/dispute', methods=['POST'])
@login_required
def dispute():
	"""
	"	Dispute real bet:
	"		This step make sure user's feed will update pending status
	"""
	try:
		handshakes = []
		shakers = []
		uid = int(request.headers['Uid'])
		user = User.find_user_with_id(uid)
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		offchain = data.get('offchain', '')
		if len(offchain) == 0:
			return response_error(MESSAGE.MISSING_OFFCHAIN, CODE.MISSING_OFFCHAIN)

		offchain = offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')

		if 'm' in offchain:
			offchain = int(offchain.replace('m', ''))
			handshake = db.session.query(Handshake).filter(and_(Handshake.id==offchain, Handshake.user_id==user.id)).first()
			if handshake is None:
				return response_error(MESSAGE.HANDSHAKE_CANNOT_REFUND, CODE.HANDSHAKE_CANNOT_REFUND)

			# check: handshake didn't match with any shaker
			if handshake.remaining_amount >= handshake.amount:
				return response_error(MESSAGE.HANDSHAKE_CANNOT_DISPUTE, CODE.HANDSHAKE_CANNOT_DISPUTE)

			handshake.bk_status = handshake.status
			handshake.status = HandshakeStatus['STATUS_DISPUTE_PENDING']
			db.session.flush()
			handshakes.append(handshake)

		elif 's' in offchain:
			offchain = int(offchain.replace('s', ''))
			shaker = db.session.query(Shaker).filter(and_(Shaker.id==offchain, Shaker.shaker_id==user.id)).first()
			if shaker is None:
				return response_error(MESSAGE.HANDSHAKE_CANNOT_REFUND, CODE.HANDSHAKE_CANNOT_REFUND)

			shaker.bk_status = shaker.status
			shaker.status = HandshakeStatus['STATUS_DISPUTE_PENDING']
			db.session.flush()
			shakers.append(shaker)
			handshake = Handshake.find_handshake_by_id(shaker.handshake_id)
			if handshake is None:
				return response_error(MESSAGE.HANDSHAKE_CANNOT_REFUND, CODE.HANDSHAKE_CANNOT_REFUND)

		db.session.commit()
		handshake_bl.update_handshakes_feed(handshakes, shakers)

		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)