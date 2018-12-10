from flask import g
from datetime import *

from app import db
from app.models import Contract

import app.constants as CONST


def all_contracts():
	c = []
	contracts = db.session.query(Contract).all()
	for contract in contracts:
		c.append(contract.to_json())
	return c


def filter_contract_id_in_contracts(j, contracts):
	if j is not None and 'contract_id' in j:
		contract_id = j['contract_id']
		del j['contract_id']
		j['contract'] = None
		for c in contracts:
			if c['id'] == contract_id:
				j['contract'] = c
				break
	return j
	

def get_active_smart_contract(contract_type=CONST.CONTRACT_TYPE['ETH']):
	if contract_type == CONST.CONTRACT_TYPE['ETH']:
		return Contract.find_contract_by_address_and_json(g.PREDICTION_SMART_CONTRACT, g.PREDICTION_JSON)
	
	return Contract.find_contract_by_address_and_json(g.ERC20_PREDICTION_SMART_CONTRACT, g.ERC20_PREDICTION_JSON)
