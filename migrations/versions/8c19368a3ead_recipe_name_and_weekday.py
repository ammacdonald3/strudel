"""Recipe name and weekday

Revision ID: 8c19368a3ead
Revises: c3db16fae5ed
Create Date: 2022-11-07 14:03:20.520515

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c19368a3ead'
down_revision = 'c3db16fae5ed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('weekday',
    sa.Column('weekday_id', sa.Integer(), nullable=False),
    sa.Column('weekday_name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('weekday_id')
    )
    op.add_column('current_meal', sa.Column('recipe_name', sa.String(), nullable=True))
    op.add_column('current_meal', sa.Column('weekday_id', sa.Integer(), nullable=True))
    op.alter_column('current_meal', 'recipe_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.create_foreign_key(None, 'current_meal', 'weekday', ['weekday_id'], ['weekday_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'current_meal', type_='foreignkey')
    op.alter_column('current_meal', 'recipe_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('current_meal', 'weekday_id')
    op.drop_column('current_meal', 'recipe_name')
    op.drop_table('weekday')
    # ### end Alembic commands ###