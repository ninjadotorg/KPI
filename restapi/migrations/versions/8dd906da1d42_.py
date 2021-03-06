"""empty message

Revision ID: 8dd906da1d42
Revises: 892aaacea275
Create Date: 2018-12-11 11:49:27.383498

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8dd906da1d42'
down_revision = '892aaacea275'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('project',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('date_modified', sa.DateTime(), nullable=True),
    sa.Column('deleted', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('type_id', sa.Integer(), nullable=True),
    sa.Column('modified_user_id', sa.Integer(), nullable=True),
    sa.Column('created_user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['modified_user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['type_id'], ['review_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('project')
    # ### end Alembic commands ###
