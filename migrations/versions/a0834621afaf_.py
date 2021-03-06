"""empty message

Revision ID: a0834621afaf
Revises: 4200cedada3f
Create Date: 2020-10-26 14:49:04.757130

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0834621afaf'
down_revision = '4200cedada3f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'seeking_venue')
    # ### end Alembic commands ###
