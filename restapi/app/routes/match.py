import os
import json
import requests
import hashlib
import app.constants as CONST
import app.bl.match as match_bl
import app.bl.contract as contract_bl
import app.bl.storage as storage_bl
import app.bl.outcome as outcome_bl

from sqlalchemy import and_, or_, desc, func
from flask_jwt_extended import jwt_required, decode_token
from flask import g, Blueprint, request, current_app as app
from collections import OrderedDict
from datetime import datetime
from app.helpers.response import response_ok, response_error
from app.helpers.decorators import login_required, admin_required
from app.helpers.utils import local_to_utc, now_to_strftime
from app.tasks import send_email_create_market, upload_file_google_storage, recombee_sync_user_data, event_image_default
from app import db, recombee_client
from app.models import User, Match, Outcome, Task, Source, Category, Contract, Handshake, Token
from app.helpers.message import MESSAGE, CODE

match_routes = Blueprint('match', __name__)

@match_routes.route('/', methods=['GET'])
@login_required
def matches():
	try:
		uid = int(request.headers['Uid'])
		source = request.args.get('source')
		keywords = request.args.get('keywords')
		response = []
		matches = []

		t = datetime.now().timetuple()
		seconds = local_to_utc(t)
		
		matches = db.session.query(Match)\
				.filter(\
					Match.deleted == 0,\
					Match.date > seconds,\
					Match.public == 1,\
					Match.id.in_(db.session.query(Outcome.match_id).filter(and_(Outcome.result == -1, Outcome.hid != None)).group_by(Outcome.match_id))
					)\
				.order_by(Match.date.asc(), Match.index.desc())\
				.all()

		# get suggested matches from recombee
		match_ids_recommended = match_bl.get_user_recommended_data(user_id=uid, offset=20, timestamp=seconds)

		# get suggested matches from algolia		
		arr_ids = match_bl.algolia_search(source, keywords)
		if arr_ids is not None and len(arr_ids) > 0:
			match_ids_recommended.extend(arr_ids)

		# sort them
		if len(match_ids_recommended) > 0:
			matches = sorted(matches, key=lambda m: m.id not in match_ids_recommended)

		for match in matches:
			arr_outcomes = outcome_bl.check_outcome_valid(match.outcomes)
			if len(arr_outcomes) > 0:
				match_json = match.to_json()

				if match.source is not None:
					source_json = match_bl.handle_source_data(match.source)
					match_json["source"] = source_json

				if match.category is not None:
					match_json["category"] = match.category.to_json()

				match_json["outcomes"] = arr_outcomes

				total_users, total_bets = match_bl.get_total_user_and_amount_by_match_id(match.id)
				if total_users == 0 and total_bets == 0:
					total_users, total_bets = match_bl.fake_users_and_bets()
					support_users, oppose_users = match_bl.fake_support_and_oppose_users(total_users)
					match_json["total_users"] = total_users
					match_json["total_bets"] = total_bets
					match_json["bets_side"] = {
						"support": support_users,
						"oppose": oppose_users
					}
				else:
					match_json["total_users"] = total_users
					match_json["total_bets"] = total_bets

					match_json["bets_side"] = {
						"support": outcome_bl.count_support_users_play_on_outcome(match.outcomes[0].id),
						"oppose": outcome_bl.count_against_users_play_on_outcome(match.outcomes[0].id)
					}
				response.append(match_json)

		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)


@match_routes.route('/add', methods=['POST'])
@login_required
def add_match():
	try:
		from_request = request.headers.get('Request-From', 'mobile')
		request_size = request.headers.get('Content-length') # string
		uid = int(request.headers['Uid'])
		token_id = request.args.get('token_id')
		file_name = None
		saved_path = None

		if request.form.get('data') is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		item = json.loads(request.form.get('data'))
		if request.files and len(request.files) > 0 and request.files['image'] is not None:
			if int(request_size) <= CONST.UPLOAD_MAX_FILE_SIZE and storage_bl.validate_extension(request.files['image'].filename, CONST.UPLOAD_ALLOWED_EXTENSIONS):
				file_name, saved_path = storage_bl.handle_upload_file(request.files['image'])
			else: 
				return response_error(MESSAGE.FILE_TOO_LARGE, CODE.FILE_TOO_LARGE)

		if token_id is None:
			contract = contract_bl.get_active_smart_contract()
			if contract is None:
				return response_error(MESSAGE.CONTRACT_EMPTY_VERSION, CODE.CONTRACT_EMPTY_VERSION)

		else:
			token = Token.find_token_by_id(token_id)
			if token is None:
				return response_error(MESSAGE.TOKEN_NOT_FOUND, CODE.TOKEN_NOT_FOUND)

			token_id = token.id
			# refresh erc20 contract
			contract = contract_bl.get_active_smart_contract(contract_type=CONST.CONTRACT_TYPE['ERC20'])
			if contract is None:
				return response_error(MESSAGE.CONTRACT_EMPTY_VERSION, CODE.CONTRACT_EMPTY_VERSION)

		response_json = []
		source = None
		category = None

		if match_bl.is_validate_match_time(item) == False:				
			return response_error(MESSAGE.MATCH_INVALID_TIME, CODE.MATCH_INVALID_TIME)

		if "source_id" in item:
			# TODO: check deleted and approved
			source = db.session.query(Source).filter(Source.id == int(item['source_id'])).first()
		elif "source" in item and "name" in item["source"] and "url" in item["source"]:
			source = db.session.query(Source).filter(and_(Source.name==item["source"]["name"], Source.url==item["source"]["url"])).first()
			if source is None:
				source = Source(
					name=item["source"]["name"],
					url=item["source"]["url"],
					created_user_id=uid
				)
				db.session.add(source)
				db.session.flush()
		else:
			if item['public'] == 1:
				return response_error(MESSAGE.MATCH_SOURCE_EMPTY, CODE.MATCH_SOURCE_EMPTY)

		if "category_id" in item:
			category = db.session.query(Category).filter(Category.id == int(item['category_id'])).first()
		else:
			if "category" in item and "name" in item["category"]:
				category = db.session.query(Category).filter(Category.name==item["category"]["name"]).first()
				if category is None:
					category = Category(
						name=item["category"]["name"],
						created_user_id=uid
					)
					db.session.add(category)
					db.session.flush()

		image_url_default = CONST.SOURCE_GC_DOMAIN.format(app.config['GC_STORAGE_BUCKET'], '{}/{}'.format(app.config.get('GC_STORAGE_FOLDER'), app.config.get('GC_DEFAULT_FOLDER')), CONST.IMAGE_NAME_SOURCE_DEFAULT)

		if source is not None and source.image_url is not None and source.image_url != '': 
			image_url_default = source.image_url

		match = Match(
			homeTeamName=item.get('homeTeamName', ''),
			homeTeamCode=item.get('homeTeamCode', ''),
			homeTeamFlag=item.get('homeTeamFlag', ''),
			awayTeamName=item.get('awayTeamName', ''),
			awayTeamCode=item.get('awayTeamCode', ''),
			awayTeamFlag=item.get('awayTeamFlag', ''),
			name=item['name'],
			public=item['public'],
			market_fee=int(item.get('market_fee', 0)),
			date=item['date'],
			reportTime=item['reportTime'],
			disputeTime=item['disputeTime'],
			created_user_id=uid,
			source_id=None if source is None else source.id,
			category_id=None if category is None else category.id,
			grant_permission=int(item.get('grant_permission', 0)),
			creator_wallet_address=item.get('creator_wallet_address'),
			outcome_name=item.get('outcome_name'),
			event_name=item.get('event_name'),
			image_url=image_url_default
		)
		db.session.add(match)
		db.session.flush()

		# Add default YES outcome
		outcome = Outcome(
			name=CONST.OUTCOME_DEFAULT_NAME,
			match_id=match.id,
			contract_id=contract.id,
			modified_user_id=uid,
			created_user_id=uid,
			token_id=token_id,
			from_request=from_request,
			approved=CONST.OUTCOME_STATUS['PENDING']
		)
		db.session.add(outcome)
		db.session.flush()

		match_json = match.to_json()
		match_json['contract'] = contract.to_json()
		match_json['source_name'] = None if source is None else source.name
		match_json['category_name'] = None if category is None else category.name

		if source is not None:
			source_json = match_bl.handle_source_data(match.source)
			match_json["source"] = source_json

		if category is not None:
			match_json["category"] = category.to_json()

		response_json.append(match_json)

		# Send mail create market
		send_email_create_market.delay(match.id, uid)

		db.session.commit()

		# Handle upload file to Google Storage
		if file_name is not None and saved_path is not None:
			upload_file_google_storage.delay(match.id, file_name, saved_path)

		return response_ok(response_json)
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@match_routes.route('/remove/<int:id>', methods=['POST'])
@login_required
@admin_required
def remove(id):
	try:
		match = Match.find_match_by_id(id)
		if match is not None:
			db.session.delete(match)
			db.session.commit()
			return response_ok(message="{} has been deleted!".format(match.id))
		else:
			return response_error(MESSAGE.MATCH_NOT_FOUND, CODE.MATCH_NOT_FOUND)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@match_routes.route('/report/<int:match_id>', methods=['POST'])
@login_required
def report_match(match_id):
	"""
	"" report: report outcomes
	"" input:
	""		match_id
	"""
	try:
		uid = int(request.headers['Uid'])
		data = request.json
		response = []
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		match = Match.find_match_by_id(match_id)
		if match is not None:
			result = data['result']
			if result is None:
				return response_error(MESSAGE.MATCH_RESULT_EMPTY, CODE.MATCH_RESULT_EMPTY)
			
			if not match_bl.is_exceed_closing_time(match.id):
				return response_error(MESSAGE.MATCH_CANNOT_SET_RESULT, CODE.MATCH_CANNOT_SET_RESULT)

			for item in result:
				if 'side' not in item:
					return response_error(MESSAGE.OUTCOME_INVALID_RESULT, CODE.OUTCOME_INVALID_RESULT)
				
				if 'outcome_id' not in item:
					return response_error(MESSAGE.OUTCOME_INVALID, CODE.OUTCOME_INVALID)

				outcome = Outcome.find_outcome_by_id(item['outcome_id'])
				if outcome is not None and outcome.created_user_id == uid:
					message, code = match_bl.is_able_to_set_result_for_outcome(outcome)
					if message is not None and code is not None:
						return message, code

					outcome.result = CONST.RESULT_TYPE['PROCESSING']
					outcome_json = outcome.to_json()
					response.append(outcome_json)

				else:
					return response_error(MESSAGE.OUTCOME_INVALID, CODE.OUTCOME_INVALID)

			return response_ok(response)
		else:
			return response_error(MESSAGE.MATCH_NOT_FOUND, CODE.MATCH_NOT_FOUND)

	except Exception, ex:
		return response_error(ex.message)


@match_routes.route('/report', methods=['GET'])
@login_required
def match_need_user_report():
	try:
		uid = int(request.headers['Uid'])

		t = datetime.now().timetuple()
		seconds = local_to_utc(t)

		response = []
		contracts = contract_bl.all_contracts()

		# Get all matchs are PENDING (-1)
		matches = db.session.query(Match).filter(and_(Match.date < seconds, Match.reportTime >= seconds, Match.id.in_(db.session.query(Outcome.match_id).filter(and_(Outcome.result == CONST.RESULT_TYPE['PENDING'], Outcome.hid != None, Outcome.created_user_id == uid)).group_by(Outcome.match_id)))).all()

		# Filter all outcome of user
		for match in matches:
			match_json = match.to_json()
			arr_outcomes = []
			for outcome in match.outcomes:
				if outcome.created_user_id == uid and outcome.hid >= 0 and outcome.approved == 1:
					outcome_json = contract_bl.filter_contract_id_in_contracts(outcome.to_json(), contracts)
					arr_outcomes.append(outcome_json)
			
			match_json["outcomes"] = arr_outcomes
			response.append(match_json)

		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)


@match_routes.route('/relevant-event', methods=['GET'])
@login_required
def relevant_events():
	try:
		match_id = int(request.args.get('match')) if request.args.get('match') is not None else None
		match = Match.find_match_by_id(match_id)

		response = []
		matches = []
		t = datetime.now().timetuple()
		seconds = local_to_utc(t)
		if match is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		matches = db.session.query(Match)\
		.filter(\
			or_(Match.source_id == match.source_id, Match.category_id == match.category_id),\
			Match.deleted == 0,\
			Match.date > seconds,\
			Match.public == 1,\
			Match.id != match_id, \
			Match.id.in_(db.session.query(Outcome.match_id).filter(and_(Outcome.result == -1, Outcome.hid != None)).group_by(Outcome.match_id)))\
		.order_by(Match.date.asc(), Match.index.desc())\
		.all()

		# Get all source_id
		source_ids = list(OrderedDict.fromkeys(list(map(lambda x: x.source_id, matches))))
		sources = db.session.query(Source)\
				.filter(\
					Source.id.in_(source_ids))\
				.all()

		for match in matches:
			match_json = match.to_json()
			arr_outcomes = outcome_bl.check_outcome_valid(match.outcomes)
			if len(arr_outcomes) > 0:
				match_json = match.to_json()

				if match.source is not None:
					source_json = match_bl.handle_source_data(match.source)
					match_json["source"] = source_json

				if match.category is not None:
					match_json["category"] = match.category.to_json()

				match_json["outcomes"] = arr_outcomes

				total_users, total_bets = match_bl.get_total_user_and_amount_by_match_id(match.id)
				if total_users == 0 and total_bets == 0:
					total_users, total_bets = match_bl.fake_users_and_bets()
					support_users, oppose_users = match_bl.fake_support_and_oppose_users(total_users)
					match_json["total_users"] = total_users
					match_json["total_bets"] = total_bets
					match_json["bets_side"] = {
						"support": support_users,
						"oppose": oppose_users
					}
				else:
					match_json["total_users"] = total_users
					match_json["total_bets"] = total_bets

					match_json["bets_side"] = {
						"support": outcome_bl.count_support_users_play_on_outcome(match.outcomes[0].id),
						"oppose": outcome_bl.count_against_users_play_on_outcome(match.outcomes[0].id)
					}
				response.append(match_json)

		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)


@match_routes.route('/<int:match_id>', methods=['GET'])
@login_required
def match_detail(match_id):
	"""
	" This endpoint will be called when user shares link to his/her friends
	"""
	try:
		outcome_id = int(request.args.get('outcome_id', -1))

		t = datetime.now().timetuple()
		seconds = local_to_utc(t)		

		match = db.session.query(Match)\
			.filter(\
				Match.id == match_id,\
				Match.deleted == 0,\
				Match.date > seconds,\
				Match.id.in_(db.session.query(Outcome.match_id).filter(and_(Outcome.result == -1, Outcome.hid > 0)).group_by(Outcome.match_id)))\
			.first()

		if match is None:
			return response_error(MESSAGE.MATCH_NOT_FOUND, CODE.MATCH_NOT_FOUND)

		arr_outcomes = outcome_bl.check_outcome_valid(match.outcomes)
		if len(arr_outcomes) > 0:
			match_json = match.to_json()

			if match.source is not None:
				source_json = match_bl.handle_source_data(match.source)
				match_json["source"] = source_json

			if match.category is not None:
				match_json["category"] = match.category.to_json()

			match_json["outcomes"] = arr_outcomes

			total_users, total_bets = match_bl.get_total_user_and_amount_by_match_id(match.id)
			if total_users == 0 and total_bets == 0:
				total_users, total_bets = match_bl.fake_users_and_bets()
				support_users, oppose_users = match_bl.fake_support_and_oppose_users(total_users)
				match_json["total_users"] = total_users
				match_json["total_bets"] = total_bets

				match_json["bets_side"] = {
					"support": support_users,
					"oppose": oppose_users
				}
			else:
				match_json["total_users"] = total_users
				match_json["total_bets"] = total_bets

				match_json["bets_side"] = {
					"support": outcome_bl.count_support_users_play_on_outcome(match.outcomes[0].id),
					"oppose": outcome_bl.count_against_users_play_on_outcome(match.outcomes[0].id)
				}
			return response_ok(match_json)

		return response_error(MESSAGE.OUTCOME_INVALID, CODE.OUTCOME_INVALID)

	except Exception, ex:
		return response_error(ex.message)


@match_routes.route('/count-event', methods=['GET'])
def count_events_based_on_source():
	"""
	" This is used for extension in order to show badge.
	"""
	try:
		source = request.args.get('source')
		code = request.args.get('code')

		if source is None:
			return response_error()

		server_key = hashlib.md5('{}{}'.format(source, g.PASSPHASE)).hexdigest()
		if server_key != code:
			return response_error()

		response = {
			"bets": 0
		}
		
		url = match_bl.clean_source_with_valid_format(source)
		t = datetime.now().timetuple()
		seconds = local_to_utc(t)

		match = db.session.query(Match)\
				.filter(\
					Match.deleted == 0,\
					Match.date > seconds,\
					Match.source_id.in_(db.session.query(Source.id).filter(Source.url.contains(url))),\
					Match.id.in_(db.session.query(Outcome.match_id).filter(and_(Outcome.result == -1)).group_by(Outcome.match_id)))\
				.all()

		if match is None:
			return response_error(MESSAGE.MATCH_NOT_FOUND, CODE.MATCH_NOT_FOUND)

		response["bets"] = len(match)
		return response_ok(response)

	except Exception, ex:
		return response_error(ex.message)
