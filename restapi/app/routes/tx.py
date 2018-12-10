# -*- coding: utf-8 -*-
import os
import sys

from flask import Blueprint, request, g
from app import db
from app.models import Tx
from datetime import datetime
from app.helpers.message import MESSAGE, CODE
from app.helpers.response import response_ok, response_error
from app.helpers.decorators import login_required, admin_required

tx_routes = Blueprint('tx', __name__)


@tx_routes.route('/', methods=['GET'])
@login_required
def tx():
	try:
		txs = db.session.query(Tx).all()
		response = []
		for tx in txs:
			response.append(tx.to_json())
		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)


@tx_routes.route('/add', methods=['POST'])
@login_required
def add():
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		response_json = []
		for item in data:
			tx = Tx(
				hash=item['hash'],
				offchain=item['offchain'],
				payload=item['payload'],
				contract_address=item['contract_address'],
				contract_method=item['contract_method'],
				chain_id=item['chain_id']
			)
			db.session.add(tx)
			db.session.flush()

			response_json.append(tx.to_json())

		db.session.commit()

		return response_ok(response_json)
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
