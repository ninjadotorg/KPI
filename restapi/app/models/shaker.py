#!/usr/bin/python
# -*- coding: utf-8 -*-

from app import db
from app.models.base import BaseModel
import app.constants as CONST

class Shaker(BaseModel):
	__tablename__ = 'shaker'
	__json_public__ = ['id', 'handshake_id', 'shaker_id', 'amount', 'contract_address', 'contract_json', 'side', 'odds', 'status', 'bk_status', 'chain_id', 'from_address', 'free_bet']

	shaker_id = db.Column(db.Integer)
	amount = db.Column(db.Numeric(36, 18))
	currency = db.Column(db.String(10))
	odds = db.Column(db.Numeric(20, 1))
	chain_id = db.Column(db.Integer,
						server_default=str(CONST.BLOCKCHAIN_NETWORK['RINKEBY']),
						default=CONST.BLOCKCHAIN_NETWORK['RINKEBY'])
	from_address = db.Column(db.String(255))
	contract_address = db.Column(db.String(255))
	contract_json = db.Column(db.String(50))
	side = db.Column(db.Integer,
					server_default=str(CONST.SIDE_TYPE['SUPPORT']),
					default=CONST.SIDE_TYPE['SUPPORT'])
	status = db.Column(db.Integer,
	                   server_default=str(CONST.Handshake['STATUS_PENDING']),
	                   default=CONST.Handshake['STATUS_PENDING'])
	bk_status = db.Column(db.Integer,
	                      server_default=str(CONST.Handshake['STATUS_PENDING']),
	                      default=CONST.Handshake['STATUS_PENDING'])
	free_bet = db.Column(db.Integer,
	                   server_default=str(0),
	                   default=0)
	from_request = db.Column(db.String(255),
							server_default=str(''),
	                      	default='')
	history_id = db.Column(db.Integer)
	handshake_id = db.Column('handshake_id', db.ForeignKey('handshake.id'))

	@classmethod
	def find_shaker_by_id(cls, _id):
		return Shaker.query.filter_by(id=_id).first()

	@classmethod
	def find_shaker_by_handshake_id(cls, _id):
		return Shaker.query.filter_by(handshake_id=_id).first()

	def __repr__(self):
		return '<shaker {}>'.format(self.id)
