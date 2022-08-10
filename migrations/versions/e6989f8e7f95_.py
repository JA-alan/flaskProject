"""empty message

Revision ID: e6989f8e7f95
Revises: 431897d7a6a4
Create Date: 2022-06-18 11:12:18.209890

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e6989f8e7f95'
down_revision = '431897d7a6a4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user_answer', 'content_type',
               existing_type=mysql.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user_answer', 'content_type',
               existing_type=mysql.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
