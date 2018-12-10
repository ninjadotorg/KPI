from app import db
from app.models.base import BaseModel

user_token = db.Table('user_token',
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                        db.Column('token_id', db.Integer, db.ForeignKey('token.id'), primary_key=True)
                        )
class User(BaseModel):
	__tablename__ = 'user'
	__json_public__ = ['id', 'email', 'name']

	fcm_token = db.Column(db.Text)
	payload = db.Column(db.Text)
	email = db.Column(db.String(255))
	name = db.Column(db.String(255))
	free_bet = db.Column(db.Integer,
						server_default=str(0),
						default=0)
	is_subscribe = db.Column(db.Integer,
							server_default=str(0),
							default=0)
	is_user_disable_popup = db.Column(db.Integer,
									server_default=str(0),
									default=0)
	invited_by_user = db.Column(db.Integer,
							server_default=str(0),
							default=0)
	played_bet = db.Column(db.Integer,
							server_default=str(0),
							default=0)
	tokens = db.relationship(
						"Token",
						secondary=user_token,
						primaryjoin='user_token.c.user_id==User.id',
						secondaryjoin='user_token.c.token_id==Token.id',
						backref=db.backref('back_tokens', lazy='dynamic'),
						lazy='dynamic')
	handshakes = db.relationship('Handshake', backref='user', primaryjoin="User.id == Handshake.user_id",
	                            lazy='dynamic')
	referral = db.relationship('Referral', backref='user', primaryjoin="User.id == Referral.user_id", 
								uselist=False)

	@classmethod
	def find_user_with_id(cls, user_id):
		return User.query.filter_by(id=user_id).first()

	def __repr__(self):
		return '<User {}>'.format(self.id)
