"""Adding pcm3b measurements

Revision ID: 3d1253397eae
Revises: 2b98328a4a89
Create Date: 2019-05-29 10:51:20.331242

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d1253397eae'
down_revision = '2b98328a4a89'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('jj_measurement', sa.Column('Rlcold', sa.Float(), nullable=True))
    op.add_column('jj_measurement', sa.Column('Rlwarm', sa.Float(), nullable=True))
    op.add_column('jj_measurement', sa.Column('Rscold', sa.Float(), nullable=True))
    op.add_column('jj_measurement', sa.Column('Rswarm', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('jj_measurement', 'Rswarm')
    op.drop_column('jj_measurement', 'Rscold')
    op.drop_column('jj_measurement', 'Rlwarm')
    op.drop_column('jj_measurement', 'Rlcold')
    # ### end Alembic commands ###