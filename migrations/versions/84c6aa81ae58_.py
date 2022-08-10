"""empty message

Revision ID: 84c6aa81ae58
Revises: a4eec268df12
Create Date: 2022-06-16 09:33:40.317374

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '84c6aa81ae58'
down_revision = 'a4eec268df12'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user_article', 'article_title',
               existing_type=mysql.VARCHAR(charset='utf8mb4', collation='utf8mb4_0900_ai_ci', length=200),
               nullable=True)
    op.alter_column('user_article', 'article_head',
               existing_type=mysql.VARCHAR(charset='utf8mb4', collation='utf8mb4_0900_ai_ci', length=200),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user_article', 'article_head',
               existing_type=mysql.VARCHAR(charset='utf8mb4', collation='utf8mb4_0900_ai_ci', length=200),
               nullable=False)
    op.alter_column('user_article', 'article_title',
               existing_type=mysql.VARCHAR(charset='utf8mb4', collation='utf8mb4_0900_ai_ci', length=200),
               nullable=False)
    # ### end Alembic commands ###