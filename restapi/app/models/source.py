#!/usr/bin/python
# -*- coding: utf-8 -*-

import app.constants as CONST

from app import db
from app.models.base import BaseModel

class Source(BaseModel):
	__tablename__ = 'source'
	__json_public__ = ['id', 'name', 'approved', 'url', 'image_url']
	
	name = db.Column(db.String(255))
	url = db.Column(db.String(255))
	approved = db.Column(db.Integer,
						server_default=str(-1),
	                   	default=-1)
	image_url = db.Column(db.String(512))
	matches = db.relationship('Match', backref='source', primaryjoin="Source.id == Match.source_id",
	                             lazy='dynamic')

	@classmethod
	def find_source_by_id(cls, sid):
		return db.session.query(Source).filter_by(id=sid).first()

	@classmethod
	def find_source_by_url(cls, url):
		return db.session.query(Source).filter(Source.url.contains(url)).all()

	def __repr__(self):
		return '<source {}, {}>'.format(self.id, self.name)
