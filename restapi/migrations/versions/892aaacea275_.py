"""empty message

Revision ID: 892aaacea275
Revises: d0600adf7057
Create Date: 2018-12-11 09:38:13.562722

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '892aaacea275'
down_revision = 'd0600adf7057'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('team',
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
    op.drop_table('team')
    # ### end Alembic commands ###
