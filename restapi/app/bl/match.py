from flask import g
from datetime import *
from urllib3 import util

from sqlalchemy import func
from algoliasearch import algoliasearch
from recombee_api_client.api_requests import RecommendItemsToUser
from app import db
from app.models import User, Handshake, Match, Outcome, Contract, Shaker, Source
from app.helpers.utils import local_to_utc
from app.helpers.message import MESSAGE, CODE
from app.constants import Handshake as HandshakeStatus
from app.core import algolia, recombee_client

import random
import app.constants as CONST


def find_best_odds_which_match_support_side(outcome_id):
	handshake = db.session.query(Handshake).filter(Handshake.outcome_id==outcome_id, Handshake.side==CONST.SIDE_TYPE['OPPOSE']).order_by(Handshake.odds.asc()).first()
	if handshake is not None:
		win_value = handshake.amount * handshake.odds
		best_odds = win_value/(win_value-handshake.amount)
		best_amount = handshake.amount * (handshake.odds - 1)
		return best_odds, best_amount
	return 0, 0


def is_exceed_report_time(match_id):
	match = Match.find_match_by_id(match_id)
	if match.reportTime is not None:
		t = datetime.now().timetuple()
		seconds = local_to_utc(t)

		if seconds > match.reportTime:
			return True
	return False


def is_exceed_closing_time(match_id):
	match = Match.find_match_by_id(match_id)
	if match.date is not None:
		t = datetime.now().timetuple()
		seconds = local_to_utc(t)
		if seconds > match.date:
			return True
	return False


def is_exceed_dispute_time(match_id):
	match = Match.find_match_by_id(match_id)
	if match.disputeTime is not None:
		t = datetime.now().timetuple()
		seconds = local_to_utc(t)

		if seconds > match.disputeTime:
			return True
	return False


def is_validate_match_time(data):
	if 'date' not in data or 'reportTime' not in data or 'disputeTime' not in data:
		return False
	
	t = datetime.now().timetuple()
	seconds = local_to_utc(t)

	if seconds >= data['date'] or seconds >= data['reportTime'] or seconds >= data['disputeTime']:
		return False

	if data['date'] < data['reportTime'] and data['reportTime'] < data['disputeTime']:
		return True
	
	return False


def is_able_to_set_result_for_outcome(outcome):
	if outcome.result == CONST.RESULT_TYPE['SUPPORT_WIN'] or \
		outcome.result == CONST.RESULT_TYPE['AGAINST_WIN'] or \
		outcome.result == CONST.RESULT_TYPE['DRAW']:

		return MESSAGE.OUTCOME_HAS_RESULT, CODE.OUTCOME_HAS_RESULT

	if outcome.result == CONST.RESULT_TYPE['PROCESSING']:
		return MESSAGE.OUTCOME_IS_REPORTING, CODE.OUTCOME_IS_REPORTING

	return None, None


def get_total_user_and_amount_by_match_id(match_id):
	# Total User
	hs_count_user = db.session.query(Handshake.user_id.label("user_id"))\
		.filter(Outcome.match_id == match_id)\
		.filter(Handshake.outcome_id == Outcome.id)\
		.filter(Handshake.status != HandshakeStatus['STATUS_PENDING'])\
		.group_by(Handshake.user_id)

	s_count_user = db.session.query(Shaker.shaker_id.label("user_id"))\
		.filter(Outcome.match_id == match_id)\
		.filter(Handshake.outcome_id == Outcome.id)\
		.filter(Handshake.id == Shaker.handshake_id)\
		.filter(Shaker.status != HandshakeStatus['STATUS_PENDING'])\
		.group_by(Shaker.shaker_id)

	user_union = hs_count_user.union(s_count_user)
	total_user = db.session.query(func.count(user_union.subquery().columns.user_id).label("total")).scalar()

	# Total Amount
	hs_amount = db.session.query(func.sum((Handshake.amount * Handshake.odds)).label("total_amount_hs"))\
		.filter(Outcome.match_id == match_id)\
		.filter(Handshake.outcome_id == Outcome.id)

	s_amount = db.session.query(func.sum((Shaker.amount * Shaker.odds)).label("total_amount_s"))\
		.filter(Outcome.match_id == match_id)\
		.filter(Handshake.outcome_id == Outcome.id)\
		.filter(Handshake.id == Shaker.handshake_id)

	total_amount = db.session.query(hs_amount.label("total_amount_hs"), s_amount.label("total_amount_s")).first()
	
	total_users = total_user if total_user is not None else 0			
	total_bets = (total_amount.total_amount_hs if total_amount.total_amount_hs is not None else 0)  + (total_amount.total_amount_s if total_amount.total_amount_s is not None else 0)

	return total_users, total_bets


def fake_users_and_bets():
	total_bets = [0.032, 0.512, 0.0345, 0.002]
	total_users = [2, 4, 1]
	return random.choice(total_users), random.choice(total_bets)


def fake_support_and_oppose_users(total_users):
	n = [2, 1, 3]
	support_users = total_users / random.choice(n)
	oppose_users = total_users - support_users
	return support_users, oppose_users


def get_domain(source):
	parsed_uri = util.parse_url(source)
	result = '{uri.netloc}'.format(uri=parsed_uri)
	return result


def clean_source_with_valid_format(source):
	result = get_domain(source)
	result = result.replace('www.', '')
	result = result.split('.')
	return result[0]


def handle_source_data(source):
	source_json = source.to_json()
	source_json["url_icon"] = CONST.SOURCE_URL_ICON.format(get_domain(source.url))
	if source_json["name"] is None or source_json["name"] == "":
		source_json["name"] = get_domain(source.url)    
	return source_json


def keyword_search(source, keywords):
	txts = []
	if keywords is not None:
		txts = keywords.split(',')

	if source is not None:
		txts.append(clean_source_with_valid_format(source))
	
	return txts


def algolia_search(source, keywords):
	txts = keyword_search(source, keywords)
	arr = []

	for txt in txts:
		response = algolia.search(txt)
		hits = response['hits']
		if hits is not None and len(hits) > 0:
			for data in hits:
				try:
					arr.append(int(data['objectID']))	
				except Exception as ex:
					print(str(ex))

		if len(arr) > 0:
			break

	return arr


def get_user_recommended_data(user_id, offset=10, timestamp=0):
	options = {
		"filter": "'closeTime' > {}".format(timestamp)
	}
	response = None
	try:
		response = recombee_client.user_recommended_data(user_id, offset, options)	
	except Exception as ex:
		print(str(ex))
	finally:
		if response is None or "recomms" not in response or len(response['recomms']) == 0:
			return []
		
		ids = list(map(lambda x : int(x["id"]), response['recomms']))
		return ids
