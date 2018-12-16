from app import db
from app.models.base import BaseModel
from sqlalchemy import func

class ReviewType(BaseModel):
	__tablename__ = 'review_type'
	__json_public__ = ['id', 'name']
	
	name = db.Column(db.String(255))
	users = db.relationship('User', backref='review_type', primaryjoin="ReviewType.id == User.type_id",
	                             lazy='dynamic')

	teams = db.relationship('Team', backref='review_type', primaryjoin="ReviewType.id == Team.type_id",
	                             lazy='dynamic')

	companies = db.relationship('Company', backref='review_type', primaryjoin="ReviewType.id == Company.type_id",
	                             lazy='dynamic')

	questions = db.relationship('Question', backref='review_type', primaryjoin="ReviewType.id == Question.type_id",
	                             lazy='dynamic')

	@classmethod
	def find_review_type_by_id(cls, type_id):
		return db.session.query(ReviewType).filter(ReviewType.id==type_id).first()

	def __repr__(self):
		return '<ReviewType {}>'.format(self.id)
