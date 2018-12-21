from app import db
from app.models.base import BaseModel
from sqlalchemy import func

class User(BaseModel):
	__tablename__ = 'user'
	__json_public__ = ['id', 'email', 'name', 'is_need_change_password', 'title', 'avatar', 'keywords']

	email = db.Column(db.String(255))
	name = db.Column(db.String(255))
	title = db.Column(db.String(255))
	password = db.Column(db.String(255))
	avatar = db.Column(db.String(255))
	keywords = db.Column(db.String(255))
	is_need_change_password = db.Column(db.Integer,
										server_default=str(1),
										default=1)
	role_id = db.Column('role_id', db.ForeignKey('role.id'))
	type_id = db.Column('type_id', db.ForeignKey('review_type.id'))

	ratings = db.relationship('Rating', backref='user', primaryjoin="User.id == Rating.user_id",
	                             lazy='dynamic')

	@classmethod
	def find_user_by_id(cls, user_id):
		return User.query.filter_by(id=user_id).first()

	@classmethod
	def find_user_by_email(cls, email):
		return User.query.filter_by(email=func.binary(email)).first()

	@classmethod
	def find_user_by_email_and_password(cls, email, password):
		return User.query.filter_by(email=func.binary(email), password=password).first()

	def __repr__(self):
		return '<User {}>'.format(self.id)
