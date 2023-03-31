"""Current_Meal recipe name removal

Revision ID: 77a7df9dc5f4
Revises: 7f78efb51d3b
Create Date: 2022-11-09 21:08:21.444630

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '77a7df9dc5f4'
down_revision = '7f78efb51d3b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('current_meal', 'recipe_name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('current_meal', sa.Column('recipe_name', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###