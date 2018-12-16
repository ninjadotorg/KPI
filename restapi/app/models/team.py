from app import db
from app.models.base import BaseModel

class Team(BaseModel):
	__tablename__ = 'team'
	__json_public__ = ['id', 'name']

	name = db.Column(db.String(255))
	desc = db.Column(db.Text)
	type_id = db.Column('type_id', db.ForeignKey('review_type.id'))
	
	@classmethod
	def find_team_by_id(cls, team_id):
		return db.session.query(Team).filter(Team.id==team_id).first()

	def __repr__(self):
		return '<Team {}>'.format(self.id)
