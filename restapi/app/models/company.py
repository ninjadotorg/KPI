from app import db
from app.models.base import BaseModel

class Company(BaseModel):
	__tablename__ = 'company'
	__json_public__ = ['id', 'name']

	name = db.Column(db.String(255))
	desc = db.Column(db.Text)
	type_id = db.Column('type_id', db.ForeignKey('review_type.id'))
	
	@classmethod
	def find_company_by_id(cls, company_id):
		return db.session.query(Company).filter(Company.id==company_id).first()
		
	def __repr__(self):
		return '<Company {}>'.format(self.id)
