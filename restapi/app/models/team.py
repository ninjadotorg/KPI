from app import db
from app.models.base import BaseModel

class Team(BaseModel):
	__tablename__ = 'team'
	__json_public__ = ['id', 'name', 'comment_count', 'rating_count']

	name = db.Column(db.String(255))
	desc = db.Column(db.Text)
	comment_count = db.Column(db.Integer,
										server_default=str(0),
										default=0)
	rating_count = db.Column(db.Integer,
										server_default=str(0),
										default=0)
	type_id = db.Column('type_id', db.ForeignKey('review_type.id'))
	
	@classmethod
	def find_team_by_id(cls, team_id):
		return db.session.query(Team).filter(Team.id==team_id).first()

	def __repr__(self):
		return '<Team {}>'.format(self.id)
