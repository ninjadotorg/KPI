#!/usr/bin/python
# -*- coding: utf-8 -*-

import app.constants as CONST

from app import db
from app.models.base import BaseModel
from app.models.contract import Contract
class Outcome(BaseModel):
	__tablename__ = 'outcome'
	__json_public__ = ['id', 'name', 'hid', 'result', 'total_amount', 'total_dispute_amount', 'index', 'contract_id', 'approved']
	name = db.Column(db.String(255))
	hid = db.Column(db.BigInteger)
	result = db.Column(db.Integer,
						server_default=str(CONST.RESULT_TYPE['PENDING']),
	                   	default=CONST.RESULT_TYPE['PENDING'])
	total_amount = db.Column(db.Numeric(36, 18))
	total_dispute_amount = db.Column(db.Numeric(36, 18))
	index = db.Column(db.Integer,
							server_default=str(1),
	                      	default=1)
	from_request = db.Column(db.String(255),
							server_default=str(''),
	                      	default='')
	approved = db.Column(db.Integer,
						server_default=str(1),
						default=1)
	match_id = db.Column('match_id', db.ForeignKey('match.id'))
	contract_id = db.Column('contract_id', db.ForeignKey('contract.id'))
	token_id = db.Column('token_id', db.ForeignKey('token.id'))
	handshakes = db.relationship('Handshake', backref='outcome', primaryjoin="Outcome.id == Handshake.outcome_id",
	                             lazy='dynamic')

	@classmethod
	def find_outcome_by_id(cls, outcome_id):
		return Outcome.query.filter_by(id=outcome_id).first()

	@classmethod
	def find_outcome_by_hid(cls, hid):
		return Outcome.query.filter_by(hid=hid).first()

	def __repr__(self):
		return '<outcome {}, {}>'.format(self.id, self.name)
