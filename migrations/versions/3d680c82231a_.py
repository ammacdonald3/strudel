"""empty message

Revision ID: 3d680c82231a
Revises: b5b25e5d363b
Create Date: 2020-10-04 21:41:08.635427

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d680c82231a'
down_revision = 'b5b25e5d363b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('recipe', sa.Column('recipe_image_url', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('recipe', 'recipe_image_url')
    # ### end Alembic commands ###
