#!/usr/bin/python
# -*- coding: utf-8 -*-

import app.constants as CONST

from app import db
from app.models.base import BaseModel

class Category(BaseModel):
	__tablename__ = 'category'
	__json_public__ = ['id', 'name']
	
	name = db.Column(db.String(255))
	approved = db.Column(db.Integer,
						server_default=str(-1),
	                   	default=-1)
	matches = db.relationship('Match', backref='category', primaryjoin="Category.id == Match.category_id",
	                             lazy='dynamic')

	@classmethod
	def find_category_by_id(cls, cate_id):
		return Category.query.filter_by(id=cate_id).first()

	def __repr__(self):
		return '<category {}, {}>'.format(self.id, self.name)
