from app import db
from app.models.base import BaseModel

class Referral(BaseModel):
	__tablename__ = 'referral_code'
	__json_public__ = ['id', 'code']

	code = db.Column(db.String(255))
	user_id = db.Column('user_id', db.ForeignKey('user.id'))

	@classmethod
	def find_referral_by_code(cls, code):
		return Referral.query.filter_by(code=code).first()

	@classmethod
	def find_referral_by_uid(cls, uid):
		return Referral.query.filter_by(user_id=uid).first()

	def __repr__(self):
		return '<Referral {}>'.format(self.id)
