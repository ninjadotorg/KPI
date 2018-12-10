from flask import Flask
from sqlalchemy import and_, func
from decimal import *
from datetime import datetime
from app.factory import make_celery
from app.core import db, configure_app, firebase, dropbox_services, mail_services, gc_storage_client, recombee_client
from app.models import Handshake, Outcome, Shaker, Match, Task, Contract, User, Setting, Referral, Source
from app.helpers.utils import utc_to_local, is_valid_email
from app.helpers.mail_content import *
from app.constants import Handshake as HandshakeStatus

import sys
import time
import app.constants as CONST
import simplejson as json
import os, hashlib
import requests
import random
import app.bl.storage as storage_bl

app = Flask(__name__)
# config app
configure_app(app)

# db
db.init_app(app)

# init firebase database
firebase.init_app(app)
mail_services.init_app(app)

# celery
celery = make_celery(app)


@celery.task()
def update_feed(handshake_id):
	try:
		handshake = Handshake.find_handshake_by_id(handshake_id)
		if handshake is None:
			print 'handshake {} is None'.format(handshake_id)
			return

		outcome = Outcome.find_outcome_by_id(handshake.outcome_id)
		if outcome is None:
			print 'outcome for handshake: {} is None'.format(handshake_id)
			return

		match = Match.find_match_by_id(outcome.match_id)
		if match is None:
			print 'match is None'
			return
		
		print '-----------------------------------------------------------'
		print 'begin: update feed for user id: {}'.format(handshake.user_id)
		print '-----------------------------------------------------------'

		_id = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + 'm' + str(handshake.id)
		amount = handshake.amount
		status = handshake.status
		bk_status = handshake.bk_status
		shakers = handshake.shakers

		shake_user_ids = []
		shake_user_infos = []
		if shakers is not None:
			for s in shakers:
				shake_user_ids.append(s.shaker_id)	
				shake_user_infos.append(s.to_json())

		hs = {
			"id": _id,
			"hid_s": outcome.hid,
			"type_i": handshake.hs_type,
			"state_i": handshake.state,
			"status_i": status,
			"bk_status_i": bk_status,
			"init_user_id_i": handshake.user_id,
			"chain_id_i": handshake.chain_id,
			"shake_user_ids_is": shake_user_ids,
			"text_search_ss": [handshake.description],
			"shake_count_i": handshake.shake_count,
			"init_at_i": int(time.mktime(handshake.date_created.timetuple())),
			"last_update_at_i": int(time.mktime(handshake.date_modified.timetuple())),
			"extra_data_s": handshake.extra_data,
			"remaining_amount_s": str(handshake.remaining_amount),
			"amount_s": str(amount),
			"outcome_id_i": handshake.outcome_id,
			"odds_f": float(handshake.odds),
			"currency_s": handshake.currency,
			"side_i": handshake.side,
			"from_address_s": handshake.from_address,
			"result_i": outcome.result,
			"free_bet_i": handshake.free_bet,
			"shakers_s": json.dumps(shake_user_infos, use_decimal=True),
			"closing_time_i": match.date,
			"reporting_time_i": match.reportTime,
			"disputing_time_i": match.disputeTime,
			"outcome_total_amount_s": '{0:f}'.format(outcome.total_amount if outcome.total_amount is not None else 0),
			"outcome_total_dispute_amount_s": '{0:f}'.format(outcome.total_dispute_amount if outcome.total_dispute_amount is not None else 0),
			"contract_address_s": handshake.contract_address,
			"contract_json_s": handshake.contract_json,
			"contract_type_s": CONST.CONTRACT_TYPE['ETH'] if outcome.token_id is None else CONST.CONTRACT_TYPE['ERC20']
		}
		print 'create maker {}'.format(hs)

		# add to firebase database
		firebase.push_data(hs, handshake.user_id)

		#  add to solr
		arr_handshakes = []
		arr_handshakes.append(hs)
		endpoint = "{}/handshake/update".format(app.config['SOLR_SERVICE'])
		data = {
			"add": arr_handshakes
		}			
		res = requests.post(endpoint, json=data)
		if res.status_code > 400 or \
			res.content is None or \
			(isinstance(res.content, str) and 'null' in res.content):
			print('SOLR service is failed. Save to task')
			task = Task(
						task_type=CONST.TASK_TYPE['NORMAL'],
						data=json.dumps(hs),
						action=CONST.TASK_ACTION['ADD_FEED'],
						status=-1
					)
			db.session.add(task)
			db.session.commit()

	except Exception as e:
		db.session.rollback()
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("add_feed=>",exc_type, fname, exc_tb.tb_lineno)


@celery.task()
def add_shuriken(user_id, shuriken_type):
	try:
		if user_id is not None:
			endpoint = "{}/api/system/betsuccess/{}".format(app.config['DISPATCHER_SERVICE_ENDPOINT'], user_id)
			params = {
				"type": str(shuriken_type)
			}
			res = requests.post(endpoint, params=params)
			print 'add_shuriken {}'.format(res)
			if res.status_code > 400:
				print('Add shuriken is failed.')


	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("add_shuriken=>",exc_type, fname, exc_tb.tb_lineno)


@celery.task()
def send_dispute_email(match_name):
	"""
	" Send email to admin in order to resolve this outcome
	"""
	try:
		# Send mail to admin
		mail_services.send(app.config['RESOLVER_EMAIL'], app.config['FROM_EMAIL'], 'Event {} need your resolve!'.format(match_name), '' )

	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("send_dispute_email=>",exc_type, fname, exc_tb.tb_lineno)


@celery.task()
def log_responsed_time():
	try:
		path = app.config['BASE_DIR']
		path = os.path.dirname(path) + '/logs/debug.log'
		dropbox_services.upload(path, "/responsed_time.csv")

	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("log_responsed_time=>",exc_type, fname, exc_tb.tb_lineno)


@celery.task()
def subscribe_email(email, match_id, fcm, payload, uid):
	"""
	" send this email when user subscribe email. We need send to dispatcher in silent mode (isNeedEmail=0)
	"""
	try:
		# Call to Dispatcher endpoint verification email
		endpoint = '{}/user/verification/email/start?email={}&isNeedEmail=0'.format(app.config["DISPATCHER_SERVICE_ENDPOINT"], email)
		data_headers = {
			"Fcm-Token": fcm,
			"Payload": payload,
			"Uid": str(uid)
		}

		res = requests.post(endpoint, headers=data_headers, json={}, timeout=10) # timeout: 10s

		if res.status_code > 400:
			print "Verify email fail: {}".format(res)
			return False

		data = res.json()

		if data['status'] == 0:
			print "Verify email fail: {}".format(data)
			return False

		# Send email
		email_body = render_email_subscribe_content(match_id)
		mail_services.send(email, app.config['FROM_EMAIL'], "You made a prediction", email_body)

		return True

	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("log_subscribe_email_time=>",exc_type, fname, exc_tb.tb_lineno)


@celery.task()
def subscribe_email_to_claim_redeem_code(email, redeem_code_1, redeem_code_2, fcm, payload, uid):
	"""
	" send this email when user subscribe email. We need send to dispatcher in silent mode (isNeedEmail=0)
	"""
	try:
		# Call to Dispatcher endpoint verification email
		endpoint = '{}/user/verification/email/start?email={}&isNeedEmail=0'.format(app.config["DISPATCHER_SERVICE_ENDPOINT"], email)
		data_headers = {
			"Fcm-Token": fcm,
			"Payload": payload,
			"Uid": str(uid)
		}

		res = requests.post(endpoint, headers=data_headers, json={}, timeout=10) # timeout: 10s

		if res.status_code > 400:
			print "Verify email fail: {}".format(res)
			return False

		data = res.json()
		if data['status'] == 0:
			print "Verify email fail: {}".format(data)
			return False

		# Send email
		r = Referral.find_referral_by_uid(uid)
		if r is not None:
			email_body = render_email_claim_redeem_code_content(redeem_code_1, redeem_code_2, '{}prediction?refer={}'.format(app.config['BASE_URL'], r.code))

			print '------- send redeem code to user {}-------'.format(email)
			mail_services.send(email, app.config['FROM_EMAIL'], "Your free predictions", email_body)

			return True
		
		return False

	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("log_subscribe_email_to_claim_redeem_code=>",exc_type, fname, exc_tb.tb_lineno)


@celery.task()
def subscribe_notification_email(email, fcm, payload, uid):
	"""
	" send this email when user input email in notification section on create market page. We need send to dispatcher in normal mode
	"""
	try:
		# Call to Dispatcher endpoint verification email
		endpoint = '{}/user/verification/email/start?email={}'.format(app.config["DISPATCHER_SERVICE_ENDPOINT"], email)
		data_headers = {
			"Fcm-Token": fcm,
			"Payload": payload,
			"Uid": str(uid)
		}

		res = requests.post(endpoint, headers=data_headers, json={}, timeout=10) # timeout: 10s

		if res.status_code > 400:
			print "Verify email fail: {}".format(res)
			return False

		data = res.json()
		if data['status'] == 0:
			print "Verify email fail: {}".format(data)
			return False

		return True

	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("log_subscribe_notification_email=>",exc_type, fname, exc_tb.tb_lineno)


@celery.task()
def send_reward_redeem(email, redeem_code, referral_link):
	"""
	" Reward user who invites friend play bet
	"""
	try:
		# Send email
		email_body = render_reward_email_content(redeem_code, referral_link)
		mail_services.send(email, app.config['FROM_EMAIL'], "Your Referral Reward", email_body)

		return True

	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("log_send_reward_redeem=>",exc_type, fname, exc_tb.tb_lineno)


@celery.task()
def send_renew_redeem_code(email, redeem_code, referral_link):
	"""
	" Renew redeem code when user clicks on refund bet
	"""
	try:
		# Send email
		email_body = render_renew_redeem_email_content(redeem_code, referral_link)
		mail_services.send(email, app.config['FROM_EMAIL'], "Your New Redeem Code", email_body)

		return True

	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("log_send_renew_redeem_code=>",exc_type, fname, exc_tb.tb_lineno)


@celery.task()
def send_email_match_result(outcome_id, uid, user_choice, outcome_result):
	"""
	" We need pass outcome_result param 'cause it still not commit to database
	"""
	try:
		outcome = Outcome.find_outcome_by_id(outcome_id)
		if outcome is None:
			print("send_email_match_result => Invalid outcome")
			return False

		user = User.find_user_with_id(uid)
		if user is not None and is_valid_email(user.email):
			# Send email
			email_body = render_result_email_content(outcome.match.name, outcome_result, user_choice)
			mail_services.send(user.email, app.config['FROM_EMAIL'], "The results of {} are in!".format(outcome.match.name), email_body)

	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("send_email_match_result=>", exc_type, fname, exc_tb.tb_lineno)


@celery.task()
def send_email_create_market(match_id, uid):
	"""
	" Inform to user the event is created and waiting for review.
	"""
	try:
		user = User.find_user_with_id(uid)
		if user is None or user.is_subscribe == 0 or is_valid_email(user.email) is False:
			print("User is invalid")
			return False
		
		match = Match.find_match_by_id(match_id)
		if match is not None:
			subject = """Your event "{}" was created successfully""".format(match.name)
			mail_services.send(user.email, app.config['FROM_EMAIL'], subject, render_create_new_market_mail_content(match_id))
		else:
			print 'Match: {} is None'.format(match_id)

	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("log_send_email_create_market=>", exc_type, fname, exc_tb.tb_lineno)


@celery.task()
def send_email_event_verification_failed(match_id, uid):
	"""
	" Inform to user the event was rejected by admin
	"""
	try:
		user = User.find_user_with_id(uid)
		if user is None or user.is_subscribe == 0 or is_valid_email(user.email) is False:
			print("User is invalid")
			return False

		match = Match.find_match_by_id(match_id)
		if match is not None:
			subject = """Your event "{}" was rejected""".format(match.name)
			mail_services.send(user.email, app.config['FROM_EMAIL'], subject, render_verification_failed_mail_content(match_id))
		else:
			print 'Match: {} is None'.format(match_id)
		
	except Exception as identifier:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("log_send_email_event_verification_failed=>", exc_type, fname, exc_tb.tb_lineno)


@celery.task()
def send_email_event_verification_success(match_id, uid):
	"""
	" Inform to user the event was approved and showed on feed.
	"""
	try:
		user = User.find_user_with_id(uid)
		if user is None or user.is_subscribe == 0 or is_valid_email(user.email) is False:
			print("User is invalid")
			return False

		r = Referral.find_referral_by_uid(uid)
		referral_link = '{}prediction?refer={}'.format(app.config['BASE_URL'], r.code)

		match = Match.find_match_by_id(match_id)
		subject = """Your event "{}" was verified""".format(match.name)
		mail_services.send(user.email, app.config['FROM_EMAIL'], subject, render_verification_success_mail_content(app.config['BASE_URL'], match.id, user.id, referral_link))
		
	except Exception as identifier:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("log_send_email_event_verification_success=>", exc_type, fname, exc_tb.tb_lineno)


@celery.task()
def update_status_feed(_id, status, amount=None, remaining_amount=None):
	try:
		endpoint = "{}/handshake/update".format(app.config['SOLR_SERVICE'])

		shake_user_ids = []
		shake_user_infos = []


		handshake = Handshake.find_handshake_by_id(_id)
		if handshake.shakers is not None:
			for s in handshake.shakers:
				shake_user_ids.append(s.shaker_id)	
				shake_user_infos.append(s.to_json())

		add_data = {
			"id": CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + 'm' + str(_id),
			"shake_user_ids_is": {"set":shake_user_ids},
			"status_i": {"set":status},
			"shakers_s": {"set":json.dumps(shake_user_infos, use_decimal=True)}
		}

		if amount is not None:
			add_data['amount_s'] = {"set":amount}

		if remaining_amount is not None:
			add_data['remaining_amount_s'] = {"set":remaining_amount}
		data = {
			"add": [add_data]
		}
		print data
		res = requests.post(endpoint, json=data)
		if res.status_code > 400 or \
			res.content is None or \
			(isinstance(res.content, str) and 'null' in res.content):
			print "Update status feed fail id: {}".format(_id)

	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("update_status_feed => ", exc_type, fname, exc_tb.tb_lineno)


@celery.task()
def upload_file_google_storage(match_id, image_name, saved_path):
	try:
		image_crop_path = None
		image_source_path = saved_path
		if storage_bl.validate_extension(image_name, CONST.CROP_ALLOWED_EXTENSIONS):
			image_source_path, image_crop_path = storage_bl.handle_crop_image(image_name, saved_path)

		match = Match.find_match_by_id(match_id)
		if match is None:
			return False

		result_upload = gc_storage_client.upload_to_storage(app.config['GC_STORAGE_BUCKET'], image_crop_path if image_crop_path is not None else image_source_path, app.config['GC_STORAGE_FOLDER'], image_name)
		if result_upload is False:
			return None
		
		storage_bl.delete_file(image_source_path)
		if image_crop_path is not None:
			storage_bl.delete_file(image_crop_path)

		image_url = CONST.SOURCE_GC_DOMAIN.format(app.config['GC_STORAGE_BUCKET'], app.config['GC_STORAGE_FOLDER'], image_name)
		match.image_url = image_url
		db.session.commit()

	except Exception as e:
		db.session.rollback()
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("upload_file_google_storage => ", exc_type, fname, exc_tb.tb_lineno)


@celery.task()
def recombee_sync_user_data(user_id, data=[], timestamp=""):
	try:
		recombee_client.sync_user_data(user_id, data, timestamp)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("recombee_sync_user_data => ", exc_type, fname, exc_tb.tb_lineno)


@celery.task()
def run_bots(outcome_id):
	"""
	" Run bots after user play bets
	"""
	try:
		setting = Setting.find_setting_by_name(CONST.SETTING_TYPE['BOT'])
		if setting is not None and setting.status == 1:
			# get master accounts
			data_file_path = os.path.join(app.config['BASE_DIR'], 'bl') + '/master-accounts.json'
			accounts = []
			with open(data_file_path, 'r') as f:
				accounts = json.load(f)

			outcome = Outcome.find_outcome_by_id(outcome_id)
			if outcome is None or outcome.hid is None:
				return False

			contract = Contract.find_contract_by_id(outcome.contract_id)
			if contract is None:
				return False

			# get all support handshakes need to be matched
			support = db.session.query(Handshake.odds, func.sum(Handshake.remaining_amount).label('support_amount'))\
									.filter(and_(Handshake.outcome_id==outcome_id,\
												Handshake.side==CONST.SIDE_TYPE['SUPPORT'], \
												Handshake.remaining_amount > 0, \
												~Handshake.from_address.in_(accounts), \
												Handshake.status == CONST.Handshake['STATUS_INITED'])) \
									.group_by(Handshake.odds) \
									.all()

			# get all oppose handshakes need to be matched
			oppose = db.session.query(Handshake.odds, func.sum(Handshake.remaining_amount).label('oppose_amount'))\
									.filter(and_(Handshake.outcome_id==outcome_id,\
												Handshake.side==CONST.SIDE_TYPE['OPPOSE'], \
												Handshake.remaining_amount > 0, \
												~Handshake.from_address.in_(accounts), \
												Handshake.status == CONST.Handshake['STATUS_INITED'])) \
									.group_by(Handshake.odds) \
									.all()

			print 'RUN BOTS FOR OUTCOME: {} with data: {}, {}'.format(outcome.id, support, oppose)
			# add bot task match with support side
			o = {}
			if support[0] is not None and support[0].support_amount > 0:
				odds = support[0].odds
				v = odds/(odds-1)
				v = float(Decimal(str(v)).quantize(Decimal('.1'), rounding=ROUND_HALF_DOWN))

				support_amount = str(support[0].support_amount)
				o['odds'] = str(v)
				o['amount'] = support_amount if support_amount < CONST.CRYPTOSIGN_MAXIMUM_MONEY else CONST.CRYPTOSIGN_MAXIMUM_MONEY
				o['side'] = CONST.SIDE_TYPE['OPPOSE']	
				o['outcome_id'] = outcome_id	
				o['hid'] = outcome.hid	
				o['match_date'] = outcome.match.date	
				o['match_name'] = outcome.match.name	
				o['outcome_name'] = outcome.name
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


			# add bot task match with oppose side
			if oppose[0] is not None and oppose[0].oppose_amount > 0:
				odds = oppose[0].odds
				v = odds/(odds-1)
				v = float(Decimal(str(v)).quantize(Decimal('.1'), rounding=ROUND_HALF_DOWN))

				oppose_amount = str(oppose[0].oppose_amount)
				o['odds'] = v
				o['amount'] = oppose_amount if oppose_amount < CONST.CRYPTOSIGN_MAXIMUM_MONEY else CONST.CRYPTOSIGN_MAXIMUM_MONEY
				o['side'] = CONST.SIDE_TYPE['SUPPORT']	
				o['outcome_id'] = outcome_id	
				o['hid'] = outcome.hid	
				o['match_date'] = outcome.match.date	
				o['match_name'] = outcome.match.name	
				o['outcome_name'] = outcome.name
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

			db.session.commit()
	except Exception as e:
		db.session.rollback()
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("run_bots => ", exc_type, fname, exc_tb.tb_lineno)


@celery.task()
def event_image_default(match_id):
	try:
		match = Match.find_match_by_id(match_id)
		if match is None or match.source_id is None:
			return False

		source = Source.find_source_by_id(match.source_id)
		if source is None:
			return False

		image_name = '{}_{}'.format(source.id, source.name).lower()
		image_name = re.sub(r'[^A-Za-z0-9\_\-\.]+', '_', image_name)
		image_name = '{}.jpg'.format(image_name)

		match.image_url = CONST.SOURCE_GC_DOMAIN.format(app.config['GC_STORAGE_BUCKET'], '{}/{}'.format(app.config['GC_STORAGE_FOLDER'], app.config['GC_DEFAULT_FOLDER']), image_name)
		db.session.commit()		

	except Exception as e:
		db.session.rollback()
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("event_image_default => ", exc_type, fname, exc_tb.tb_lineno)
