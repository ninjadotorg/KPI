import os
import json
import app.constants as CONST

from flask import Blueprint, request, current_app as app
from app.helpers.response import response_ok, response_error
from app.helpers.decorators import login_required, admin_required
from app import db
from app.models import Contract
from app.helpers.message import MESSAGE, CODE

contract_routes = Blueprint('contract', __name__)

@contract_routes.route('/', methods=['GET'])
@login_required
def contracts():
	try:
		contracts = Contract.query.all()
		data = []

		for contract in contracts:
			data.append(contract.to_json())

		return response_ok(data)
	except Exception, ex:
		return response_error(ex.message)


@contract_routes.route('/add', methods=['POST'])
@admin_required
def add():
	try:
		uid = int(request.headers['Uid'])
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		response_json = []
		for item in data:
			contract = Contract(
				contract_name=item['contract_name'],
				contract_address=item['contract_address'],
				json_name=item['json_name']
			)
			db.session.add(contract)
			db.session.flush()

			response_json.append(contract.to_json())

		db.session.commit()
		return response_ok(response_json)
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@contract_routes.route('/remove/<int:id>', methods=['POST'])
@admin_required
def remove(id):
	try:
		contract = db.session.query(Contract).filter(Contract.id==id).first()
		if contract is not None:
			db.session.delete(contract)
			db.session.commit()
			return response_ok(message="{} has been deleted!".format(contract.id))
		else:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
