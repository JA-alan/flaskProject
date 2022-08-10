"""empty message

Revision ID: c38f1fa98f89
Revises: 118db60c1b00
Create Date: 2022-06-18 17:23:47.084928

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c38f1fa98f89'
down_revision = '118db60c1b00'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_article', sa.Column('title', sa.String(length=200), nullable=True))
    op.add_column('user_article', sa.Column('head', sa.String(length=200), nullable=True))
    op.add_column('user_article', sa.Column('content', sa.TEXT(), nullable=False))
    op.drop_column('user_article', 'article_title')
    op.drop_column('user_article', 'article_head')
    op.drop_column('user_article', 'article_content')
    op.add_column('user_function', sa.Column('title', sa.String(length=200), nullable=True))
    op.add_column('user_function', sa.Column('content', sa.TEXT(), nullable=False))
    op.drop_column('user_function', 'function_title')
    op.drop_column('user_function', 'function_content')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_function', sa.Column('function_content', mysql.TEXT(), nullable=False))
    op.add_column('user_function', sa.Column('function_title', mysql.VARCHAR(length=200), nullable=True))
    op.drop_column('user_function', 'content')
    op.drop_column('user_function', 'title')
    op.add_column('user_article', sa.Column('article_content', mysql.TEXT(), nullable=False))
    op.add_column('user_article', sa.Column('article_head', mysql.VARCHAR(charset='utf8mb4', collation='utf8mb4_0900_ai_ci', length=200), nullable=True))
    op.add_column('user_article', sa.Column('article_title', mysql.VARCHAR(charset='utf8mb4', collation='utf8mb4_0900_ai_ci', length=200), nullable=True))
    op.drop_column('user_article', 'content')
    op.drop_column('user_article', 'head')
    op.drop_column('user_article', 'title')
    # ### end Alembic commands ###