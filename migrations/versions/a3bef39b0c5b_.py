"""empty message

Revision ID: a3bef39b0c5b
Revises: 3d680c82231a
Create Date: 2020-10-10 11:25:22.812616

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3bef39b0c5b'
down_revision = '3d680c82231a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('app_user', sa.Column('admin', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('app_user', 'admin')
    # ### end Alembic commands ###
