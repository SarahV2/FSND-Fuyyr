"""empty message

Revision ID: 2d8039f2b4d3
Revises: 783ab7f6c6b3
Create Date: 2020-10-26 14:21:35.090093

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d8039f2b4d3'
down_revision = '783ab7f6c6b3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'seeking_venue')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_venue', sa.BOOLEAN(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
