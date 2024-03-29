"""chef id removal

Revision ID: 7f78efb51d3b
Revises: d6fb6a88fb03
Create Date: 2022-11-08 18:27:08.615674

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f78efb51d3b'
down_revision = 'd6fb6a88fb03'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('current_meal_chef_id_fkey', 'current_meal', type_='foreignkey')
    op.drop_column('current_meal', 'chef_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('current_meal', sa.Column('chef_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('current_meal_chef_id_fkey', 'current_meal', 'app_user', ['chef_id'], ['id'])
    # ### end Alembic commands ###
