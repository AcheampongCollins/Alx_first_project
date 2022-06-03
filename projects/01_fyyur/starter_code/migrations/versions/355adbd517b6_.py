"""empty message

Revision ID: 355adbd517b6
Revises: 36156b1d1ebf
Create Date: 2022-06-02 19:52:04.107804

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '355adbd517b6'
down_revision = '36156b1d1ebf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('website_link', sa.String(length=120), nullable=True))
    op.add_column('Venue', sa.Column('seeking_talent', sa.Boolean(), nullable=False))
    op.add_column('Venue', sa.Column('seeking_description', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'seeking_description')
    op.drop_column('Venue', 'seeking_talent')
    op.drop_column('Venue', 'website_link')
    # ### end Alembic commands ###