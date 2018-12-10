#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy.event import listen
from app import db
from app.core import slack_service
from app.models.base import BaseModel

class Match(BaseModel):
	__tablename__ = 'match'
	__json_public__ = ['id', 'date', 'reportTime', 'disputeTime', 'outcomes', 'name', 'outcome_name', 'event_name', 'public', 'market_fee', 'grant_permission', 'source_id', 'category_id', 'creator_wallet_address', 'created_user_id', 'image_url', 'comment_count']
	__json_modifiers__ = {
        'outcomes': lambda outcomes, _: [outcome.to_json() for outcome in outcomes]
    }
	homeTeamName = db.Column(db.String(255))
	homeTeamCode = db.Column(db.String(10))
	homeTeamFlag = db.Column(db.String(512))
	awayTeamName = db.Column(db.String(255))
	awayTeamCode = db.Column(db.String(10))
	awayTeamFlag = db.Column(db.String(512))
	name = db.Column(db.String(512))
	outcome_name = db.Column(db.String(512))
	event_name = db.Column(db.String(512))
	homeScore = db.Column(db.Integer)
	awayScore = db.Column(db.Integer)
	market_fee = db.Column(db.Integer,
							server_default=str(1),
	                      	default=1)
	date = db.Column(db.BigInteger) #closingTime

	reportTime = db.Column(db.BigInteger)
	disputeTime = db.Column(db.BigInteger)
	index = db.Column(db.Integer,
							server_default=str(1),
	                      	default=1)
	public = db.Column(db.Integer,
						server_default=str(1),
						default=0)
	# this field help admin set outcome for creator
	grant_permission = db.Column(db.Integer,
						server_default=str(0),
						default=0)
	creator_wallet_address = db.Column(db.String(255))
	image_url = db.Column(db.String(512))
	comment_count = db.Column(db.Integer)
	category_id = db.Column('category_id', db.ForeignKey('category.id'))
	source_id = db.Column('source_id', db.ForeignKey('source.id'))
	outcomes = db.relationship('Outcome', backref='match', primaryjoin="Match.id == Outcome.match_id", lazy='dynamic')

	@classmethod
	def find_match_by_id(cls, match_id):
		return Match.query.filter_by(id=match_id).first()

	def __repr__(self):
		return '<match {}, {}, {}>'.format(self.id, self.homeTeamName, self.awayTeamName)


def remind_review_market(mapper, connection, target):
	if target.created_user_id is not None and target.created_user_id > 0:
		message = '{} - match id: {}, closing time: {}'.format(target.name, target.id, target.date)
		slack_service.send_message(message)

listen(Match, 'after_insert', remind_review_market)