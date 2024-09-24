"""empty message

Revision ID: 7019b8bd2682
Revises: 7ef4f4646c6f
Create Date: 2024-09-24 18:15:23.953624

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7019b8bd2682'
down_revision = '7ef4f4646c6f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('owner',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('car',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('color', sa.Enum('yellow', 'blue', 'gray', name='color_enum'), nullable=False),
    sa.Column('model', sa.Enum('hatch', 'sedan', 'convertible', name='model_enum'), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['owner.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('car')
    op.drop_table('owner')
    # ### end Alembic commands ###
