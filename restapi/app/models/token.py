#!/usr/bin/python
# -*- coding: utf-8 -*-

import app.constants as CONST

from app import db
from app.models.base import BaseModel

class Token(BaseModel):
	__tablename__ = 'token'
	__json_public__ = ['id', 'tid', 'symbol', 'name', 'decimal', 'status', 'contract_address']
	
	tid = db.Column(db.Integer)
	symbol = db.Column(db.String(20))
	name = db.Column(db.String(50))
	decimal = db.Column(db.Integer)
	contract_address = db.Column(db.String(255))
	status = db.Column(db.Integer,
						server_default=str(CONST.TOKEN_STATUS['PENDING']),
						default=CONST.TOKEN_STATUS['PENDING'])

	outcomes = db.relationship('Outcome', backref='token', primaryjoin="Token.id == Outcome.token_id", lazy='dynamic')

	@classmethod
	def find_token_by_id(cls, _id):
		return Token.query.filter_by(id=_id).first()

	@classmethod
	def find_token_by_symbol(cls, symbol):
		return Token.query.filter_by(symbol=symbol).first()

	def __repr__(self):
		return '<token {}, {}>'.format(self.id, self.tid)
