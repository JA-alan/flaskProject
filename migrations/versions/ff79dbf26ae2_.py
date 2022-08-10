"""empty message

Revision ID: ff79dbf26ae2
Revises: 22a37febe690
Create Date: 2022-07-01 15:31:00.954020

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff79dbf26ae2'
down_revision = '22a37febe690'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('portrait', sa.String(length=200), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'portrait')
    # ### end Alembic commands ###