"""empty message

Revision ID: 92f25063b2b1
Revises: c38f1fa98f89
Create Date: 2022-06-19 09:50:42.275642

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92f25063b2b1'
down_revision = 'c38f1fa98f89'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('title', table_name='root_diary')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('title', 'root_diary', ['title'], unique=False)
    # ### end Alembic commands ###