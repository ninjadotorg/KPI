#!/usr/bin/python
# -*- coding: utf-8 -*-

import app.constants as CONST

from app import db
from app.models.base import BaseModel

class History(BaseModel):
	__tablename__ = 'history'
	__json_public__ = ['id', 'chain_id', 'description', 'from_address', 'amount']

	chain_id = db.Column(db.Integer,
						server_default=str(CONST.BLOCKCHAIN_NETWORK['RINKEBY']),
						default=CONST.BLOCKCHAIN_NETWORK['RINKEBY'])
	description = db.Column(db.Text)
	free_bet = db.Column(db.Integer,
							server_default=str(0),
	                      	default=0)
	from_address = db.Column(db.String(255))
	contract_address = db.Column(db.String(255))
	contract_json = db.Column(db.String(50))
	odds = db.Column(db.Numeric(20, 1))
	amount = db.Column(db.Numeric(36, 18))
	currency = db.Column(db.String(10))
	from_request = db.Column(db.String(255),
							server_default=str(''),
	                      	default='')
	side = db.Column(db.Integer,
						server_default=str(CONST.SIDE_TYPE['SUPPORT']),
	                   	default=CONST.SIDE_TYPE['SUPPORT'])
	user_id = db.Column(db.Integer)
	outcome_id = db.Column(db.Integer)

	def __repr__(self):
		return '<history {}>'.format(self.id)
