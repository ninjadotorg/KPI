import time

from app import db
from sqlalchemy import func, and_

from app.models import ReviewType, Rating, Question, Comment
from app.helpers.utils import utc_to_local

def count_rating_for_object(o, review_type):
	rt = db.session.query(ReviewType).filter(ReviewType.name==func.binary(review_type)).first()
	rows = db.session.query(func.sum(Rating.point).label('point'), func.count(Rating.id).label('rows')).filter(and_(Rating.object_id==o.id, Rating.question_id.in_(db.session.query(Question.id).filter(Question.type_id==rt.id)))).all()

	if rows is not None and \
		rows[0].point is not None and \
		rows[0].rows is not None:

		return rows[0].point / rows[0].rows

	return 0


def count_comments_for_object(o, review_type):
	rt = db.session.query(ReviewType).filter(ReviewType.name==func.binary(review_type)).first()
	c = db.session.query(func.count(Comment.id).label('comments')).filter(Rating.id.in_(db.session.query(Rating.id).filter(and_(Rating.object_id==o.id, Rating.question_id.in_(db.session.query(Question.id).filter(Question.type_id==rt.id)))))).group_by(Comment.id).first()
	
	if c is not None and len(c) == 1:
		return c[0]

	return 0