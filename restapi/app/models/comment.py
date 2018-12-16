from app import db
from app.models.base import BaseModel

class Comment(BaseModel):
	__tablename__ = 'comment'
	__json_public__ = ['id', 'desc']

	desc = db.Column(db.Text)
	rating_id = db.Column('rating_id', db.ForeignKey('rating.id'))
	
	def __repr__(self):
		return '<Comment {}>'.format(self.id)
