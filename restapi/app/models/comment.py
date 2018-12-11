from app import db
from app.models.base import BaseModel

class Comment(BaseModel):
	__tablename__ = 'comment'
	__json_public__ = ['id', 'desc']

	desc = db.Column(db.Text)
	object_id = db.Column(db.Integer)
	user_id = db.Column('user_id', db.ForeignKey('user.id'))
	
	def __repr__(self):
		return '<Comment {}>'.format(self.id)
