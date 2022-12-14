"""empty message

Revision ID: ad6847ffd2a7
Revises: 65c8cdb464dc
Create Date: 2022-06-11 10:40:49.775640

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad6847ffd2a7'
down_revision = '65c8cdb464dc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('user', sa.String(length=200), nullable=True),
    sa.Column('name', sa.String(length=200), nullable=True),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=200), nullable=True),
    sa.Column('phone', sa.Integer(), nullable=False),
    sa.Column('user_type', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=50), nullable=False),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone'),
    sa.UniqueConstraint('token'),
    sa.UniqueConstraint('user'),
    sa.UniqueConstraint('user_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    # ### end Alembic commands ###
