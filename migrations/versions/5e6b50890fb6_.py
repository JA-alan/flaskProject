"""empty message

Revision ID: 5e6b50890fb6
Revises: 92f25063b2b1
Create Date: 2022-06-22 12:16:47.652258

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e6b50890fb6'
down_revision = '92f25063b2b1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('email_captcha', sa.Column('author_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'email_captcha', 'users', ['author_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'email_captcha', type_='foreignkey')
    op.drop_column('email_captcha', 'author_id')
    # ### end Alembic commands ###