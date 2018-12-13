from app import db
from sqlalchemy import func, and_

from app.models import ReviewType, User, Project, Team, Company, Rating, Comment, Question
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


def is_answer_question(user_id, review_type, object_id):
	if review_type is None or \
		object_id is None or \
		user_id is None:
		return False

	rt = db.session.query(ReviewType).filter(ReviewType.name==func.binary(review_type)).first()
	if rt is None:
		return False

	result = db.session.query(Rating).filter(and_(Rating.user_id==user_id, Rating.object_id==object_id, Rating.question_id.in_(db.session.query(Question.id).filter(Question.type_id==rt.id)))).first()
	if result is None:
		return False

	result = db.session.query(Comment).filter(Comment.user_id==user_id, Comment.type_id==rt.id, Comment.object_id==object_id).first()
	if result is None:
		return False

	return True