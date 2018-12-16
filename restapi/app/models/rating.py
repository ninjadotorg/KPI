from app import db
from app.models.base import BaseModel

class Rating(BaseModel):
	__tablename__ = 'rating'
	__json_public__ = ['id', 'point']

	point = db.Column(db.Numeric(2, 1))
	object_id = db.Column(db.Integer)
	question_id = db.Column('question_id', db.ForeignKey('question.id'))
	user_id = db.Column('user_id', db.ForeignKey('user.id'))
	comments = db.relationship('Comment', backref='rating', primaryjoin="Rating.id == Comment.rating_id",
	                             lazy='dynamic')
	
	def __repr__(self):
		return '<Rating {}>'.format(self.id)
