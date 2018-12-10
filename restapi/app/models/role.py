from app import db
from app.models.base import BaseModel

class Role(BaseModel):
	__tablename__ = 'role'
	__json_public__ = ['id', 'name']

	name = db.Column(db.String(255))
	users = db.relationship('User', backref='role', primaryjoin="Role.id == User.role_id",
	                             lazy='dynamic')

	def __repr__(self):
		return '<Role {}>'.format(self.id)
