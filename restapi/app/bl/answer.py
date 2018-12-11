from app import db
from sqlalchemy import func

from app.models import ReviewType, User, Project, Team, Company
from app.constants import Type

def is_valid_object_id(review_type, object_id):
	if review_type is None or \
		object_id is None:
		return False

	rt = db.session.query(ReviewType).filter(ReviewType.name==func.binary(review_type)).first()
	if rt is None:
		return False

	result = None
	if review_type == Type['People']:
		result = db.session.query(User).filter(User.id==object_id, User.type_id==rt.id).first()

	elif review_type == Type['Project']:
		result = db.session.query(Project).filter(Project.id==object_id, Project.type_id==rt.id).first()

	elif review_type == Type['Team']:
		result = db.session.query(Team).filter(Team.id==object_id, Team.type_id==rt.id).first()

	elif review_type == Type['Company']:
		result = db.session.query(Company).filter(Company.id==object_id, Company.type_id==rt.id).first()

	if result is None:
		return False

	return True
