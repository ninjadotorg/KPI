from app import db
from app.models.base import BaseModel

class Project(BaseModel):
	__tablename__ = 'project'
	__json_public__ = ['id', 'name']

	name = db.Column(db.String(255))
	type_id = db.Column('type_id', db.ForeignKey('review_type.id'))
	
	def __repr__(self):
		return '<Project {}>'.format(self.id)
