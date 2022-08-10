"""empty message

Revision ID: a4eec268df12
Revises: 3bd6fe7ae174
Create Date: 2022-06-16 09:32:45.991222

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a4eec268df12'
down_revision = '3bd6fe7ae174'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_function',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('function_id', sa.String(length=200), nullable=False),
    sa.Column('function_title', sa.String(length=200), nullable=True),
    sa.Column('function_content', sa.TEXT(), nullable=False),
    sa.Column('label_id', sa.Integer(), nullable=True),
    sa.Column('browse_number', sa.Integer(), nullable=True),
    sa.Column('likes_number', sa.Integer(), nullable=True),
    sa.Column('collection_number', sa.Integer(), nullable=True),
    sa.Column('Photo', sa.String(length=200), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('function_id')
    )
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
    op.drop_table('user_function')
    # ### end Alembic commands ###