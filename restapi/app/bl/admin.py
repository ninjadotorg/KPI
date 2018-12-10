
from app.models import Task, Contract

import json
import app.constants as CONST
import app.bl.contract as contract_bl


def add_create_market_task(match):
	# get active contract
	contract = contract_bl.get_active_smart_contract()
	if contract is None:
		return None

	# add task
	task = Task(
		task_type=CONST.TASK_TYPE['REAL_BET'],
		data=json.dumps(match.to_json()),
		action=CONST.TASK_ACTION['CREATE_MARKET'],
		status=-1,
		contract_address=contract.contract_address,
		contract_json=contract.json_name
	)
	return task


def is_contract_support_report_for_creator_method(name):
	arr = name.split('v')
	if len(arr) == 2:
		nums = arr[1].split('_')
		number = int('{}{}'.format(nums[0], nums[1]))
		if number >= 14: #support version from 1.4
			return True

	return False


def can_admin_report_this_outcome(outcome):
	if outcome is None or outcome.result != CONST.RESULT_TYPE['PENDING'] or outcome.hid is None:
		return False
	
	contract = Contract.find_contract_by_id(outcome.contract_id)
	if contract is None:
		return False

	# created by admin
	if outcome.created_user_id is None:
		return True

	if is_contract_support_report_for_creator_method(contract.json_name) is False:
		return False

	if outcome.match.grant_permission == 1 and \
		outcome.match.creator_wallet_address is not None and \
		len(outcome.match.creator_wallet_address) > 0:
		return True

	return False