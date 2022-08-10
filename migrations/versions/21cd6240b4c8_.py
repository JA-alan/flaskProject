"""empty message

Revision ID: 21cd6240b4c8
Revises: d908a45bec55
Create Date: 2022-06-15 10:22:40.250967

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '21cd6240b4c8'
down_revision = 'd908a45bec55'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_article',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('article_id', sa.Integer(), nullable=False),
    sa.Column('article_title', sa.String(length=200), nullable=True),
    sa.Column('article_head', sa.String(length=200), nullable=True),
    sa.Column('article_content', sa.TEXT(), nullable=False),
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
    sa.UniqueConstraint('article_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_article')
    # ### end Alembic commands ###
