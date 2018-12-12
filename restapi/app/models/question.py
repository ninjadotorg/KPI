from app import db
from app.models.base import BaseModel

class Question(BaseModel):
	__tablename__ = 'question'
	__json_public__ = ['id', 'name']

	name = db.Column(db.String(255))
	type_id = db.Column('type_id', db.ForeignKey('review_type.id'))
	ratings = db.relationship('Rating', backref='question', primaryjoin="Question.id == Rating.question_id",
	                             lazy='dynamic')
	
	def __repr__(self):
		return '<Question {}>'.format(self.id)
