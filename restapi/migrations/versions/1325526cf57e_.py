"""empty message

Revision ID: 1325526cf57e
Revises: 3c3f2fe36a21
Create Date: 2018-12-15 16:00:51.774287

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1325526cf57e'
down_revision = '3c3f2fe36a21'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('rating_id', sa.Integer(), nullable=True))
    op.drop_constraint(u'comment_ibfk_4', 'comment', type_='foreignkey')
    op.drop_constraint(u'comment_ibfk_3', 'comment', type_='foreignkey')
    op.create_foreign_key(None, 'comment', 'rating', ['rating_id'], ['id'])
    op.drop_column('comment', 'user_id')
    op.drop_column('comment', 'question_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('question_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.add_column('comment', sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'comment', type_='foreignkey')
    op.create_foreign_key(u'comment_ibfk_3', 'comment', 'user', ['user_id'], ['id'])
    op.create_foreign_key(u'comment_ibfk_4', 'comment', 'question', ['question_id'], ['id'])
    op.drop_column('comment', 'rating_id')
    # ### end Alembic commands ###
