"""empty message

Revision ID: 6d2808fe49c8
Revises: b9ef523f8c98
Create Date: 2018-12-12 09:30:37.014269

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d2808fe49c8'
down_revision = 'b9ef523f8c98'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('type_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'comment', 'review_type', ['type_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'comment', type_='foreignkey')
    op.drop_column('comment', 'type_id')
    # ### end Alembic commands ###
