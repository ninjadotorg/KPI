#!/usr/bin/python
# -*- coding: utf-8 -*-
import hashlib
import os
import sys
import time
import requests
import json
import app.constants as CONST
import app.bl.match as match_bl
import app.bl.outcome as outcome_bl
import app.bl.referral as referral_bl
import app.bl.redeem as redeem_bl

from decimal import *
from datetime import datetime
from flask import g
from app import db, fcm, sg, firebase
from sqlalchemy import and_, or_, func, text, not_
from app.constants import Handshake as HandshakeStatus, CRYPTOSIGN_OFFCHAIN_PREFIX
from app.models import Handshake, User, Shaker, Outcome, Match
from app.helpers.bc_exception import BcException
from app.tasks import update_feed, add_shuriken, send_dispute_email, send_email_event_verification_success, send_email_match_result, run_bots
from app.helpers.message import MESSAGE
from app.helpers.utils import utc_to_local, local_to_utc

getcontext().prec = 18


def save_status_all_bet_which_user_win(user_id, outcome):
	handshakes = []
	shakers = []
	if outcome.result == CONST.RESULT_TYPE['DRAW'] or outcome.result == CONST.RESULT_TYPE['PENDING']:
		return None, None

	handshakes = db.session.query(Handshake).filter(or_(and_(Handshake.status==HandshakeStatus['STATUS_COLLECT_FAILED'], Handshake.user_id==user_id, Handshake.outcome_id==outcome.id, Handshake.side==outcome.result), and_(Handshake.status==HandshakeStatus['STATUS_INITED'], Handshake.user_id==user_id, Handshake.outcome_id==outcome.id, Handshake.side==outcome.result), and_(Handshake.status==HandshakeStatus['STATUS_COLLECT_PENDING'], Handshake.user_id==user_id, Handshake.outcome_id==outcome.id, Handshake.side==outcome.result))).all()
	shakers = db.session.query(Shaker).filter(or_(and_(Shaker.status==HandshakeStatus['STATUS_COLLECT_FAILED'], Shaker.shaker_id==user_id, Shaker.side==outcome.result, Shaker.handshake_id.in_(db.session.query(Handshake.id).filter(Handshake.outcome_id==outcome.id))), and_(Shaker.status==HandshakeStatus['STATUS_COLLECT_PENDING'], Shaker.shaker_id==user_id, Shaker.side==outcome.result, Shaker.handshake_id.in_(db.session.query(Handshake.id).filter(Handshake.outcome_id==outcome.id))), and_(Shaker.status==HandshakeStatus['STATUS_SHAKER_SHAKED'], Shaker.shaker_id==user_id, Shaker.side==outcome.result, Shaker.handshake_id.in_(db.session.query(Handshake.id).filter(Handshake.outcome_id==outcome.id))))).all()

	for handshake in handshakes:
		handshake.bk_status = handshake.status
		handshake.status = HandshakeStatus['STATUS_DONE']
		db.session.merge(handshake)

	for shaker in shakers:
		shaker.bk_status = shaker.status
		shaker.status = HandshakeStatus['STATUS_DONE']
		db.session.merge(shaker)

	db.session.flush()
	return handshakes, shakers

def save_collect_state_for_maker(handshake):
	if handshake is not None:
		outcome = Outcome.find_outcome_by_id(handshake.outcome_id)
		if outcome is not None:
			if handshake.side == outcome.result:
				shaker = Shaker.find_shaker_by_handshake_id(handshake.id)
				if shaker is not None:
					shaker.bk_status = shaker.status
					shaker.status = HandshakeStatus['STATUS_DONE']

					db.session.merge(shaker)
					db.session.flush()
					handshakes, shakers = save_status_all_bet_which_user_win(handshake.user_id, outcome)
					
					if shakers is None:
						shakers = []	
					shakers.append(shaker)
					return handshakes, shakers
	return None, None

def save_collect_state_for_shaker(shaker):
	if shaker is not None:
		handshake = Handshake.find_handshake_by_id(shaker.handshake_id)
		outcome = Outcome.find_outcome_by_id(handshake.outcome_id)

		if outcome is not None:
			if shaker.side == outcome.result:
				handshake.bk_status = handshake.status
				handshake.status = HandshakeStatus['STATUS_DONE']

				db.session.merge(handshake)
				db.session.flush()
				handshakes, shakers = save_status_all_bet_which_user_win(shaker.shaker_id, outcome)
				
				if handshakes is None:
					handshakes = []
				handshakes.append(handshake)
				return handshakes, shakers

	return None, None

def save_refund_state_for_all(user_id, outcome_id):
	outcome = Outcome.find_outcome_by_id(outcome_id)
	handshakes = db.session.query(Handshake).filter(and_(Handshake.status.in_([HandshakeStatus['STATUS_REFUND_PENDING'], HandshakeStatus['STATUS_INITED']]), Handshake.user_id==user_id, Handshake.outcome_id==outcome_id)).all()
	shakers = db.session.query(Shaker).filter(and_(Shaker.status==HandshakeStatus['STATUS_REFUND_PENDING'], Shaker.shaker_id==user_id, Shaker.handshake_id.in_(db.session.query(Handshake.id).filter(Handshake.outcome_id==outcome_id)))).all()
	
	for hs in handshakes:
		hs.bk_status = hs.status
		hs.status = HandshakeStatus['STATUS_REFUNDED']
		db.session.merge(hs)

	for sk in shakers:
		sk.bk_status = sk.status
		sk.status = HandshakeStatus['STATUS_REFUNDED']
		db.session.merge(sk)

	return handshakes, shakers


def save_disputed_state(outcome_id):
	handshakes = []
	shakers = []
	handshakes = db.session.query(Handshake).filter(Handshake.outcome_id == outcome_id, Handshake.remaining_amount < Handshake.amount).all()
	handshake_ids = list(map(lambda x: x.id, handshakes))
	shakers = db.session.query(Shaker).filter(Shaker.handshake_id.in_(handshake_ids)).all()

	for hs in handshakes:
		hs.status = HandshakeStatus['STATUS_DISPUTED']
		db.session.merge(hs)

	for shaker in shakers:
		shaker.status = HandshakeStatus['STATUS_DISPUTED']
		db.session.merge(shaker)

	db.session.flush()
	return handshakes, shakers


def save_resolve_state_for_outcome(outcome_id):
	handshakes = []
	shakers = []
	handshakes = db.session.query(Handshake).filter(Handshake.outcome_id == outcome_id).all()
	handshake_ids = list(map(lambda x: x.id, handshakes))
	shakers = db.session.query(Shaker).filter(Shaker.handshake_id.in_(handshake_ids)).all()

	for hs in handshakes:
		hs.bk_status = hs.status
		hs.status = HandshakeStatus['STATUS_RESOLVED']
		db.session.merge(hs)

	for shaker in shakers:
		shaker.bk_status = shaker.status
		shaker.status = HandshakeStatus['STATUS_RESOLVED']
		db.session.merge(shaker)

	db.session.flush()
	return handshakes, shakers


def save_user_disputed_state(handshake, user_id, side, outcome_result):
	# Update STATUS_USER_DISPUTED
	# No need to update bk_status

	handshakes = []
	shakers = []
	side_arr = [side] if outcome_result != CONST.RESULT_TYPE['DRAW'] else [CONST.RESULT_TYPE['SUPPORT_WIN'], CONST.RESULT_TYPE['AGAINST_WIN']]

	handshakes = db.session.query(Handshake).filter(Handshake.side.in_(side_arr), Handshake.user_id == user_id, Handshake.outcome_id == handshake.outcome_id).all()
	for hs in handshakes:
		hs.status = HandshakeStatus['STATUS_USER_DISPUTED']
		db.session.merge(hs)

	shakers = db.session.query(Shaker).filter(Shaker.side.in_(side_arr), Shaker.shaker_id == user_id, Shaker.handshake_id.in_(db.session.query(Handshake.id).filter(Handshake.outcome_id==handshake.outcome_id).group_by(Handshake.id))).all()
	for shaker in shakers:
		shaker.status = HandshakeStatus['STATUS_USER_DISPUTED']
		db.session.merge(shaker)

	db.session.flush()
	return handshakes, shakers


def has_valid_shaker(handshake):
	if handshake is not None:
		shakers = handshake.shakers.all()
		if shakers is not None:
			for sk in shakers:
				if sk.status == HandshakeStatus['STATUS_SHAKER_SHAKED']:
					return True
	return False


def data_need_set_result_for_outcome(outcome):
	if outcome.result == -1:
		return None, None

	handshakes = db.session.query(Handshake).filter(Handshake.outcome_id==outcome.id).all()
	shakers = db.session.query(Shaker).filter(Shaker.handshake_id.in_(db.session.query(Handshake.id).filter(Handshake.outcome_id==outcome.id))).all()
	
	for hs in handshakes:
		if not has_valid_shaker(hs) and hs.status == HandshakeStatus['STATUS_INITED']:
			hs.bk_status = hs.status
			hs.status = HandshakeStatus['STATUS_MAKER_SHOULD_UNINIT']
			db.session.merge(hs)
			db.session.flush()

	return handshakes, shakers


# when time exceed report time and there is no result or outcome result is draw
def can_refund(handshake, shaker=None):
	if handshake is None and shaker is None:
		return False

	outcome = None
	if handshake is not None:
		if handshake.status == HandshakeStatus['STATUS_REFUNDED']:
			return False

		outcome = Outcome.find_outcome_by_id(handshake.outcome_id)

	else:
		if shaker.status == HandshakeStatus['STATUS_REFUNDED']:
			return False
		
		handshake = Handshake.find_handshake_by_id(shaker.handshake_id)
		outcome = Outcome.find_outcome_by_id(handshake.outcome_id)


	if outcome is not None and outcome.hid is not None:
		if outcome.result == CONST.RESULT_TYPE['DRAW'] or (match_bl.is_exceed_report_time(outcome.match_id) and outcome.result == -1):
			return True
	return False


def parse_inputs(inputs):
	offchain = ''
	hid = ''
	state = -1
	outcome_result = None

	if 'offchain' in inputs:
		offchain = inputs['offchain']

	if 'hid' in inputs:
		hid = inputs['hid']

	if 'state' in inputs:
		state = inputs['state']

	if 'outcome' in inputs:
		outcome_result = inputs['outcome']

	return offchain, hid, state, outcome_result


def update_amount_for_outcome(outcome_id, user_id, side, outcome_result):
	side_arr = ', '.join([str(x) for x in ([side] if outcome_result != 3 else [1, 2])])

	outcome = Outcome.find_outcome_by_id(outcome_id)
	dispute_amount_query_m = "(SELECT SUM(amount) AS total FROM (SELECT amount FROM handshake WHERE handshake.outcome_id = {} AND handshake.side IN ({}) AND handshake.user_id = {} AND handshake.status IN ({},{},{})) AS tmp) AS total_dispute_amount_m".format(outcome.id, side_arr, user_id, HandshakeStatus['STATUS_USER_DISPUTED'], HandshakeStatus['STATUS_DISPUTED'], HandshakeStatus['STATUS_DISPUTE_PENDING'])
	dispute_amount_query_s = '(SELECT SUM(total_amount) AS total FROM (SELECT shaker.amount as total_amount FROM handshake JOIN shaker ON handshake.id = shaker.handshake_id WHERE handshake.outcome_id = {} AND shaker.side IN ({}) AND shaker.shaker_id = {} AND shaker.status IN ({},{},{})) AS tmp) AS total_dispute_amount_s'.format(outcome.id, side_arr, user_id, HandshakeStatus['STATUS_USER_DISPUTED'], HandshakeStatus['STATUS_DISPUTED'], HandshakeStatus['STATUS_DISPUTE_PENDING'])
	amount_query_m = '(SELECT SUM(amount) AS total FROM (SELECT amount FROM handshake WHERE handshake.outcome_id = {} AND handshake.side IN ({})) AS tmp) AS total_amount_m'.format(outcome.id, side_arr)
	amount_query_s = '(SELECT SUM(total_amount) AS total FROM (SELECT shaker.amount as total_amount FROM handshake JOIN shaker ON handshake.id = shaker.handshake_id WHERE handshake.outcome_id = {} AND shaker.side IN ({})) AS tmp) AS total_amount_s'.format(outcome.id, side_arr)

	total_amount = db.engine.execute('SELECT {}, {}, {}, {}'.format(dispute_amount_query_m, dispute_amount_query_s, amount_query_m, amount_query_s)).first()

	outcome.total_dispute_amount = (total_amount['total_dispute_amount_m'] if total_amount['total_dispute_amount_m'] is not None else 0) + (total_amount['total_dispute_amount_s'] if total_amount['total_dispute_amount_s'] is not None else 0)
	outcome.total_amount = (total_amount['total_amount_m'] if total_amount['total_amount_m'] is not None else 0) + (total_amount['total_amount_s'] if total_amount['total_amount_s'] is not None else 0)
	db.session.flush()


def save_handshake_method_for_event(method, inputs):
	offchain, hid, state, outcome_result = parse_inputs(inputs)
	if method == 'init' or method == 'initTestDrive':
		offchain = offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')
		offchain = int(offchain.replace('m', ''))
		handshake = Handshake.find_handshake_by_id(offchain)
		if handshake is not None:
			handshake.bk_status = handshake.status
			handshake.status = HandshakeStatus['STATUS_INIT_FAILED']
			db.session.flush()

			arr = []
			arr.append(handshake)
			return arr, None

	elif method == 'shake' or method == 'shakeTestDrive':
		offchain = offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')
		offchain = int(offchain.replace('s', ''))
		shaker = Shaker.find_shaker_by_id(offchain)
		if shaker is not None:
			if shaker.status == HandshakeStatus['STATUS_PENDING']:
				shaker = rollback_shake_state(shaker)

			shaker.bk_status = shaker.status
			shaker.status = HandshakeStatus['STATUS_SHAKE_FAILED']
			db.session.flush()

			arr = []
			arr.append(shaker)
			return None, arr

	elif method == 'uninit' or method == 'uninitTestDrive':
		offchain = offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')
		offchain = int(offchain.replace('m', ''))
		handshake = Handshake.find_handshake_by_id(offchain)
		if handshake is not None:
			handshake.bk_status = handshake.status
			handshake.status = HandshakeStatus['STATUS_MAKER_UNINIT_FAILED']
			db.session.flush()

			arr = []
			arr.append(handshake)
			return arr, None

	elif method == 'collect' or method == 'collectTestDrive':
		offchain = offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')

		if 'm' in offchain:
			offchain = int(offchain.replace('m', ''))
			handshake = Handshake.find_handshake_by_id(offchain)
			if handshake is not None:
				handshake.bk_status = handshake.status
				handshake.status = HandshakeStatus['STATUS_COLLECT_FAILED']
				db.session.flush()

				arr = []
				arr.append(handshake)
				return arr, None

		elif 's' in offchain:
			offchain = int(offchain.replace('s', ''))
			shaker = Shaker.find_shaker_by_id(offchain)
			if shaker is not None:
				shaker.bk_status = shaker.status
				shaker.status = HandshakeStatus['STATUS_COLLECT_FAILED']
				db.session.flush()

				arr = []
				arr.append(shaker)
				return None, arr

	elif method == 'refund':
		offchain = offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')

		if 'm' in offchain:
			offchain = int(offchain.replace('m', ''))
			handshake = Handshake.find_handshake_by_id(offchain)
			if handshake is not None:
				handshake.bk_status = handshake.status
				handshake.status = HandshakeStatus['STATUS_REFUND_FAILED']
				db.session.flush()

				arr = []
				arr.append(handshake)
				return arr, None

		elif 's' in offchain:
			offchain = int(offchain.replace('s', ''))
			shaker = Shaker.find_shaker_by_id(offchain)
			if shaker is not None:
				shaker.bk_status = shaker.status
				shaker.status = HandshakeStatus['STATUS_REFUND_FAILED']
				db.session.flush()

				arr = []
				arr.append(shaker)
				return None, arr

	elif method == 'report':
		outcome_id, result = offchain.replace('cryptosign_report', '').split('_')
		if outcome_id is None:
			return None, None
		print 'report fail with outcome_id {}'.format(outcome_id)
		outcome = Outcome.find_outcome_by_id(outcome_id)

		if outcome is not None and outcome.result == CONST.RESULT_TYPE['PROCESSING']:
    			outcome.result = CONST.RESULT_TYPE['REPORT_FAILED']
			db.session.flush()

	elif method == 'resolve':
		outcome_id, result = offchain.replace('cryptosign_resolve', '').split('_')
		if outcome_id is None:
			return None, None
		print 'resolve fail with outcome_id {}'.format(outcome_id)
		outcome = Outcome.find_outcome_by_id(outcome_id)

		if outcome is not None and outcome.result == CONST.RESULT_TYPE['DISPUTED']:
			outcome.result = CONST.RESULT_TYPE['REPORT_FAILED']
			db.session.flush()

	return None, None


def save_failed_handshake_method_for_event(method, tx):
	if method == 'init' or method == 'initTestDrive':
		offchain = tx.offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')
		offchain = int(offchain.replace('m', ''))
		handshake = Handshake.find_handshake_by_id(offchain)
		if handshake is not None:
			handshake.status = HandshakeStatus['STATUS_INIT_FAILED']
			db.session.flush()

			arr = []
			arr.append(handshake)
			return arr, None

	elif method == 'shake' or method == 'shakeTestDrive':
		offchain = tx.offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')
		offchain = int(offchain.replace('s', ''))
		shaker = Shaker.find_shaker_by_id(offchain)
		if shaker is not None:
			if shaker.status == HandshakeStatus['STATUS_PENDING']:
				shaker = rollback_shake_state(shaker)

			shaker.status = HandshakeStatus['STATUS_SHAKE_FAILED']
			db.session.flush()

			arr = []
			arr.append(shaker)
			return None, arr

	elif method == 'report':
		payload = tx.payload
		data = json.loads(payload)

		if '_options' in data:
			options = data['_options']
			if 'onchainData' in options:
				onchain = options['onchainData']
				if 'hid' in onchain:
					hid = int(onchain['hid'])
					outcome = Outcome.find_outcome_by_hid(hid)
					if outcome is not None and outcome.result == CONST.RESULT_TYPE['PROCESSING']:
						outcome.result = CONST.RESULT_TYPE['REPORT_FAILED']
						db.session.flush()

		return None, None

	return None, None


def save_handshake_for_event(event_name, inputs):
	offchain, hid, state, outcome_result = parse_inputs(inputs)
	offchain = offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')

	if event_name == '__createMarket':
		print '__createMarket'
		offchain = int(offchain.replace('createMarket', ''))
		outcome = Outcome.find_outcome_by_id(offchain)
		if outcome is not None:
			outcome.hid = hid

			if 'closingTime' in inputs and \
				'reportTime' in inputs and \
				'disputeTime' in inputs:
				m = Match.find_match_by_id(outcome.match_id)
				m.date = int(inputs['closingTime'])
				m.reportTime = int(inputs['reportTime'])
				m.disputeTime = int(inputs['disputeTime'])

			db.session.flush()

			if outcome_bl.is_outcome_created_by_user(outcome):
				send_email_event_verification_success.delay(outcome.match_id, outcome.created_user_id)

		return None, None

	elif event_name == '__report':
		print '__report'
		# report{outcome_id}_{side}
		# side 1: SUPPORT, 2: OPPOSE, 3: DRAW
		outcome_id, result = offchain.replace('report', '').split('_')
		if outcome_id is None or result is None:
			return None, None
		
		outcome = Outcome.find_outcome_by_id(outcome_id)
		if len(result) > -1 and outcome is not None:
			result = int(result)
			outcome.result = result
			db.session.flush()

			handshakes, shakers = data_need_set_result_for_outcome(outcome)

			# send result email to users who play in
			send_result_email(outcome.id, result)

			return handshakes, shakers

		return None, None

	elif event_name == '__shake':
		print '__shake'
		offchain = offchain.replace('s', '')
		shaker = Shaker.find_shaker_by_id(int(offchain))
		if shaker is not None:
			shaker.status = HandshakeStatus['STATUS_SHAKER_SHAKED']
			shaker.bk_status = HandshakeStatus['STATUS_SHAKER_SHAKED']
			db.session.flush()

			# Add shuriken
			if shaker.free_bet == 1:
				add_shuriken.delay(shaker.shaker_id, CONST.SHURIKEN_TYPE['FREE'])
			else:
				add_shuriken.delay(shaker.shaker_id, CONST.SHURIKEN_TYPE['REAL'])


			# Run bots
			h = Handshake.find_handshake_by_id(shaker.handshake_id)
			if h is not None:
				run_bots.delay(h.outcome_id)


			# Give redeem code for referral user
			u = User.find_user_with_id(shaker.shaker_id)
			if u is not None and u.played_bet == 0:
				referral_bl.give_redeem_code_for_referred_user(shaker.shaker_id)
				u.played_bet = 1
				db.session.flush()

			arr = []
			arr.append(shaker)

			return None, arr

		return None, None

	elif event_name == '__collect':
		print '__collect'

		if 's' in offchain:
			offchain = offchain.replace('s', '')
			shaker = Shaker.find_shaker_by_id(int(offchain))
			if shaker is not None:
				# update status of shaker and handshake to done
				# find all bets belongs to this outcome which user join
				# update all statuses (shaker and handshake) of them to done
				return save_collect_state_for_shaker(shaker)

		elif 'm' in offchain:
			offchain = offchain.replace('m', '')
			handshake = Handshake.find_handshake_by_id(int(offchain))
			if handshake is not None:
				# update status of shaker and handshake to done
				# find all bets belongs to this outcome which user join
				# update all statuses (shaker and handshake) of them to done
				return save_collect_state_for_maker(handshake)

		return None, None

	elif event_name == '__init':
		print '__init'
		offchain = offchain.replace('m', '')
		handshake = Handshake.find_handshake_by_id(int(offchain))
		if handshake is not None:
			handshake.status = HandshakeStatus['STATUS_INITED']
			handshake.bk_status = HandshakeStatus['STATUS_INITED']

			db.session.flush()

			arr = []
			arr.append(handshake)

			# Add shuriken
			if handshake.free_bet == 1:
				add_shuriken.delay(handshake.user_id, CONST.SHURIKEN_TYPE['FREE'])
			else:
				add_shuriken.delay(handshake.user_id, CONST.SHURIKEN_TYPE['REAL'])

			# Run bots
			run_bots.delay(handshake.outcome_id)

			# Give redeem code for referral user
			u = User.find_user_with_id(handshake.user_id)
			if u is not None and u.played_bet == 0:
				referral_bl.give_redeem_code_for_referred_user(handshake.user_id)
				u.played_bet = 1
				db.session.flush()

			return arr, None

		return None, None

	elif event_name == '__uninit':
		print '__uninit'
		offchain = offchain.replace('m', '')
		handshake = Handshake.find_handshake_by_id(int(offchain))
		if handshake is not None:
			handshake.status = HandshakeStatus['STATUS_MAKER_UNINITED']
			handshake.bk_status = HandshakeStatus['STATUS_MAKER_UNINITED']		
			db.session.flush()

			arr = []
			arr.append(handshake)
			return arr, None
		return None, None

	elif event_name == '__refund':
		print '__refund'
		handshake = None
		user_id = None
		free_bet = False
		if 's' in offchain:
			offchain = offchain.replace('s', '')
			shaker = Shaker.find_shaker_by_id(int(offchain))
			if shaker is None:
				return None, None

			user_id = shaker.shaker_id
			free_bet = shaker.free_bet
			handshake = Handshake.find_handshake_by_id(shaker.handshake_id)

		elif 'm' in offchain:
			offchain = offchain.replace('m', '')
			handshake = Handshake.find_handshake_by_id(int(offchain))
			user_id = handshake.user_id
			free_bet = handshake.free_bet
		
		if handshake is None or user_id is None:
			return None, None
		
		if free_bet is True:
			redeem_bl.issue_new_redeem_code_for_user(user_id)
			
		return save_refund_state_for_all(user_id, handshake.outcome_id)

	elif event_name == '__dispute':
		print '__dispute'
		shaker_dispute = []
		handshake_dispute = []
		handshake = None
		user_id = None
		side = None

		if outcome_result is None:
			return None, None

		if state < 2:
			return None, None

		if 's' in offchain:
			offchain = offchain.replace('s', '')
			shaker = Shaker.find_shaker_by_id(int(offchain))
			user_id = shaker.shaker_id
			side = shaker.side

			if shaker is not None:
				handshake = Handshake.find_handshake_by_id(shaker.handshake_id)

		elif 'm' in offchain:
			offchain = offchain.replace('m', '')
			handshake = Handshake.find_handshake_by_id(int(offchain))
			user_id = handshake.user_id
			side = handshake.side

		if handshake is None or user_id is None:
			return None, None

		outcome = Outcome.find_outcome_by_id(handshake.outcome_id)
		if outcome is None:
			return None, None

		update_amount_for_outcome(outcome.id, user_id, side, outcome_result)

		if state == 3 and outcome.result != CONST.RESULT_TYPE['DISPUTED']:
			outcome.result = CONST.RESULT_TYPE['DISPUTED']
			db.session.flush()
			handshake_dispute, shaker_dispute = save_disputed_state(outcome.id)

			# Send mail to admin
			send_dispute_email.delay(outcome.match.name)

		else:
			handshake_dispute, shaker_dispute = save_user_disputed_state(handshake, user_id, side, outcome_result)

		return handshake_dispute, shaker_dispute

	elif event_name == '__resolve':
		# resolve{outcome_id}_{side}
		print '__resolve'
		outcome_id, result = offchain.replace('resolve', '').split('_')
		if outcome_id is None or result is None:
			return None, None

		# 1: SUPPORT, 2: OPPOSE, 3: DRAW: It's depended on smart contract definition.
		if len(result) == 0 or int(result) not in [1, 2, 3]:
			return None, None
		outcome = Outcome.find_outcome_by_id(outcome_id)
		if outcome is None:
			return None, None

		result = int(result)
		outcome.total_dispute_amount = 0
		outcome.result = result
		db.session.flush()
		
		handshakes, shakers = save_resolve_state_for_outcome(outcome.id)

		# send result email to users who play in
		send_result_email(outcome.id, result)
		return handshakes, shakers


def verify_taker_odds(taker_odds, maker_odds):
	if (float(taker_odds) * 10000) >= (float(maker_odds) * 100) * (float(taker_odds) * 100 - 100):
		return True

	return False


def find_all_matched_handshakes(side, odds, outcome_id, amount, maker):
	outcome = db.session.query(Outcome).filter(and_(Outcome.result==CONST.RESULT_TYPE['PENDING'], Outcome.id==outcome_id)).first()
	if outcome is not None:
		win_value = amount*odds
		if win_value - amount > 0:
			# calculate matched odds
			v = odds/(odds-1)
			v = float(Decimal(str(v)).quantize(Decimal('.1'), rounding=ROUND_HALF_DOWN))

			print 'matched odds --> {}'.format(v)
			query = text('''SELECT * FROM handshake where outcome_id = {} and odds <= {} and remaining_amount > 0 and status = {} and side != {} ORDER BY odds ASC;'''.format(outcome_id, v, CONST.Handshake['STATUS_INITED'], side))
			handshakes = []
			result_db = db.engine.execute(query)
			for row in result_db:
				if(verify_taker_odds(row['odds'], odds)):
					if maker != row['user_id']:
						handshake = Handshake(
							id=row['id'],
							hs_type=row['hs_type'],
							extra_data=row['extra_data'],
							description=row['description'],
							chain_id=row['chain_id'],
							user_id=row['user_id'],
							outcome_id=row['outcome_id'],
							odds=row['odds'],
							amount=row['amount'],
							currency=row['currency'],
							side=row['side'],
							remaining_amount=row['remaining_amount'],
							from_address=row['from_address'],
							shake_count=row['shake_count'],
							date_created=row['date_created'],
							date_modified=row['date_modified']
						)
						handshakes.append(handshake)
			return handshakes
	return []


def find_all_joined_handshakes(side, outcome_id):
	outcome = db.session.query(Outcome).filter(and_(Outcome.result==CONST.RESULT_TYPE['PENDING'], Outcome.id==outcome_id)).first()
	if outcome is not None:
		handshakes = db.session.query(Handshake).filter(and_(Handshake.side!=side, Handshake.outcome_id==outcome_id, Handshake.remaining_amount>0, Handshake.status==CONST.Handshake['STATUS_INITED'])).order_by(Handshake.odds.desc()).all()
		return handshakes
	return []


def find_available_support_handshakes(outcome_id):
	outcome = db.session.query(Outcome).filter(and_(Outcome.result==CONST.RESULT_TYPE['PENDING'], Outcome.id==outcome_id)).first()
	if outcome is not None:
		handshakes = db.session.query(Handshake.odds, func.sum(Handshake.remaining_amount).label('amount')).filter(and_(Handshake.side==CONST.SIDE_TYPE['SUPPORT'], Handshake.outcome_id==outcome_id, Handshake.remaining_amount>0, Handshake.status==CONST.Handshake['STATUS_INITED'])).group_by(Handshake.odds).order_by(Handshake.odds.desc()).all()
		if handshakes is not None and len(handshakes) > 0:
			return handshakes

		default_handshake = Handshake(
								amount=Decimal('0'),
								odds=Decimal('2.0')
							)
		response = []
		response.append(default_handshake)
		return response	

	return []


def find_available_against_handshakes(outcome_id):
	outcome = db.session.query(Outcome).filter(and_(Outcome.result==CONST.RESULT_TYPE['PENDING'], Outcome.id==outcome_id)).first()
	if outcome is not None:
		handshakes = db.session.query(Handshake.odds, func.sum(Handshake.remaining_amount).label('amount')).filter(and_(Handshake.side==CONST.SIDE_TYPE['OPPOSE'], Handshake.outcome_id==outcome_id, Handshake.remaining_amount>0, Handshake.status==CONST.Handshake['STATUS_INITED'])).group_by(Handshake.odds).order_by(Handshake.odds.desc()).all()
		if handshakes is not None and len(handshakes) > 0:
			return handshakes

		default_handshake = Handshake(
								amount=Decimal('0'),
								odds=Decimal('2.0')
							)
		response = []
		response.append(default_handshake)
		return response

	return []


def rollback_shake_state(shaker):
	if shaker is None:
		raise Exception(MESSAGE.SHAKER_NOT_FOUND)

	shaker.status = HandshakeStatus['STATUS_SHAKER_ROLLBACK']
	handshake = db.session.query(Handshake).filter(and_(Handshake.id==shaker.handshake_id, Handshake.status==HandshakeStatus['STATUS_INITED'])).first()
	if handshake is None:
		raise Exception(MESSAGE.HANDSHAKE_NOT_FOUND)

	handshake.remaining_amount += ((shaker.odds * shaker.amount) - shaker.amount)
	db.session.flush()

	return shaker


def is_init_pending_status(handshake):
	if handshake.status == HandshakeStatus['STATUS_PENDING'] and handshake.bk_status == HandshakeStatus['STATUS_PENDING']:
		return True	
	return False


def update_handshakes_feed(handshakes, shakers):
	# update feed
	if handshakes is not None:
		for handshake in handshakes:
			update_feed.delay(handshake.id)

	if shakers is not None:
		for shaker in shakers:
			update_feed.delay(shaker.handshake_id)


def can_withdraw(handshake, shaker=None):
	outcome = None
	result = None

	if shaker is None:
		if handshake is not None:
			if handshake.status == HandshakeStatus['STATUS_INITED'] or handshake.status == HandshakeStatus['STATUS_RESOLVED']:
				outcome = Outcome.find_outcome_by_id(handshake.outcome_id)
				result = handshake.side
			else:
				return MESSAGE.CANNOT_WITHDRAW
		else:
			return MESSAGE.CANNOT_WITHDRAW
	else:
		if shaker.status == HandshakeStatus['STATUS_SHAKER_SHAKED'] or shaker.status == HandshakeStatus['STATUS_RESOLVED']:
			handshake = Handshake.find_handshake_by_id(shaker.handshake_id)
			outcome = Outcome.find_outcome_by_id(handshake.outcome_id)	
			result = shaker.side
		else:
			return MESSAGE.CANNOT_WITHDRAW

	if outcome is not None:
		if outcome.result != result:
			return MESSAGE.HANDSHAKE_NOT_THE_SAME_RESULT

		if match_bl.is_exceed_dispute_time(outcome.match_id) == False:
			return MESSAGE.HANDSHAKE_WITHDRAW_AFTER_DISPUTE
	else:
		return MESSAGE.OUTCOME_INVALID

	return ''


def can_uninit(handshake):
	if handshake is None:
		return False
	
	n = time.mktime(datetime.now().timetuple())
	if len(handshake.shakers.all()) == 0:
		# avoid maker uninit too fast
		if handshake.free_bet == 1:
			ds = time.mktime(utc_to_local(handshake.date_created.timetuple()))
			if n - ds < 300.0: #5 minutes
				return False

	else:
		for sk in handshake.shakers.all():
			if sk.status == HandshakeStatus['STATUS_SHAKER_SHAKED']:
				return False
			else:
				ds = time.mktime(utc_to_local(sk.date_created.timetuple()))
				if n - ds < 300.0:
					return False

	return True


def get_total_real_bets():
	chain_info_path = os.path.abspath(os.path.dirname(__file__)) + '/user-info.json'
	data = []
	with open(chain_info_path, 'r') as f:
		data = json.load(f)
	user_address = data['userAddress']

	# Total User
	hs = db.session.query(Handshake)\
		.filter(Handshake.status != HandshakeStatus['STATUS_PENDING'])\
		.filter(Handshake.free_bet != 1)\
		.filter(~Handshake.from_address.in_(user_address))\
		.all()

	total_bets = len(hs)
	return total_bets


def all_master_accounts():
	"""
	" wallet addresses of admin
	"""
	data_file_path = os.path.abspath(os.path.dirname(__file__)) + '/master-accounts.json'
	accounts = []
	with open(data_file_path, 'r') as f:
		accounts = json.load(f)
	return accounts


def send_result_email(outcome_id, outcome_result):
	"""
	" Send result email to all users play in.
	"""
	total_users = all_users_play_in_outcome(outcome_id)
	for item in total_users:
		if hasattr(item, 'user_id') and item.user_id is not None:
			send_email_match_result.delay(outcome_id, item.user_id, item.side, outcome_result)


def all_users_play_in_outcome(outcome_id):
	# get all users who played in ended outcome.
	hs_user = db.session.query(Handshake.user_id.label('user_id'), Handshake.side.label('side'))\
		.filter(Outcome.result > 0)\
		.filter(Handshake.outcome_id == outcome_id)\
		.group_by(Handshake.user_id, Outcome.result, Handshake.side)

	s_user = db.session.query(Shaker.shaker_id.label("user_id"),Shaker.side.label('side'))\
		.filter(Outcome.result > 0)\
		.filter(Handshake.outcome_id == outcome_id)\
		.filter(Shaker.handshake_id == Handshake.id)\
		.group_by(Shaker.shaker_id, Outcome.result, Shaker.side)

	total_users = hs_user.union_all(s_user).group_by('user_id', 'side').all()
	return total_users