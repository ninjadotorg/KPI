import time

from app import db
from sqlalchemy import func, and_
from datetime import datetime

from app.models import ReviewType, User, Team, Company, Rating, Question, Comment
from app.constants import Type
from app.helpers.utils import utc_to_local

def is_valid_object_id(review_type, object_id):
	if review_type is None or \
		object_id is None:
		return None

	rt = db.session.query(ReviewType).filter(ReviewType.name==func.binary(review_type)).first()
	if rt is None:
		return None

	result = None
	if review_type == Type['People']:
		result = db.session.query(User).filter(User.id==object_id, User.type_id==rt.id).first()

	elif review_type == Type['Team']:
		result = db.session.query(Team).filter(Team.id==object_id, Team.type_id==rt.id).first()

	elif review_type == Type['Company']:
		result = db.session.query(Company).filter(Company.id==object_id, Company.type_id==rt.id).first()

	return result


def is_answer_question(user_id, review_type, object_id, question_id):
	if review_type is None or \
		object_id is None or \
		user_id is None or \
		question_id is None:
		return False

	rt = db.session.query(ReviewType).filter(ReviewType.name==func.binary(review_type)).first()
	if rt is None:
		return False

	result = db.session.query(Rating).filter(and_(Rating.user_id==user_id, Rating.object_id==object_id, Rating.question_id==question_id)).first()
	if result is None:
		return False
	else:
		n = time.mktime(datetime.now().timetuple())
		ds = time.mktime(utc_to_local(result.date_created.timetuple()))
		if n - ds > 60*60*24*30: #30 days
			return False

	return True


def review_type(comment_id):
	review_type = db.session.query(ReviewType).filter(ReviewType.id.in_(db.session.query(Question.type_id).filter(Question.id.in_(db.session.query(Rating.question_id).filter(Rating.id.in_(db.session.query(Comment.rating_id).filter(Comment.id==comment_id))))))).first()
	return review_type