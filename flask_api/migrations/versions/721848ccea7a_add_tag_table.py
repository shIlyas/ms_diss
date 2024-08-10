"""Add Tag table

Revision ID: 721848ccea7a
Revises: 30983e40068e
Create Date: 2024-07-31 12:13:46.546277

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '721848ccea7a'
down_revision = '30983e40068e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('assistant_tags',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('tag', sa.Text(), nullable=False),
    sa.Column('scenario_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['scenario_id'], ['assistant_scenarios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('assistant_tags')
    # ### end Alembic commands ###
