from app import db
from app.models.base import BaseModel

import app.constants as CONST
import json


class Tx(BaseModel):
	__tablename__ = 'tx'
	__json_public__ = ['id', 'hash', 'contract_address', 'contract_method',
	                   'payload', 'status', 'chain_id']

	hash = db.Column(db.String(255))
	contract_address = db.Column(db.String(255))
	contract_method = db.Column(db.String(255))
	payload = db.Column(db.Text)
	status = db.Column(db.Integer,
	                   server_default=str(CONST.Tx['STATUS_PENDING']),
	                   default=CONST.Tx['STATUS_PENDING'])
	offchain = db.Column(db.String(255))
	chain_id = db.Column(db.Integer, default=CONST.BLOCKCHAIN_NETWORK['RINKEBY'], server_default=str(CONST.BLOCKCHAIN_NETWORK['RINKEBY']))

	@classmethod
	def find_tx_by_id(cls, tx_id):
		return Tx.query.filter_by(id=tx_id).first()

	def __repr__(self):
		return '<Tx {}>'.format(self.hash)
