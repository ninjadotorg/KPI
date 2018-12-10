#!/usr/bin/python
# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declared_attr
from app import db
from app.helpers import JsonSerializer

class BaseModel(db.Model, JsonSerializer):
	__abstract__ = True
	id = db.Column(db.Integer, primary_key=True)
	date_created = db.Column(db.DateTime, default=db.func.utc_timestamp())
	date_modified = db.Column(db.DateTime, default=db.func.utc_timestamp(), onupdate=db.func.utc_timestamp())
	deleted = db.Column(db.Integer, default=0)

	@declared_attr
	def created_user_id(cls):
		return db.Column('created_user_id', db.ForeignKey('user.id'))

	@declared_attr
	def created_user(cls):
		return db.relationship('User', foreign_keys='%s.c.created_user_id' % cls.__tablename__, uselist=False)

	@declared_attr
	def modified_user_id(cls):
		return db.Column('modified_user_id', db.ForeignKey('user.id'))

	@declared_attr
	def modified_user(cls):
		return db.relationship('User', foreign_keys='%s.c.modified_user_id' % cls.__tablename__, uselist=False)

	def __init__(self, **kwargs):
		for k, v in kwargs.iteritems():
			if hasattr(self, k):
				setattr(self, k, v)

# @db.event.listens_for(BaseModel, "before_insert", propagate=True)
# def on_before_insert(mapper, connection, target):
#   try:
#     target.created_user_id = g.user.id
#   except Exception, ex:
#     app.logger.exception(ex)

# @db.event.listens_for(BaseModel, "before_update", propagate=True)
# def on_before_update(mapper, connection, target):
#   try:
#     target.modifed_user_id = g.user.id
#   except Exception, ex:
#     app.logger.exception(ex)
